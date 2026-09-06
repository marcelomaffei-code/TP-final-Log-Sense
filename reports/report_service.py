from datetime import datetime
from collections import defaultdict
import re

class ReportService:
    def __init__(self, tree):
        self.tree = tree
    
    def occurrences_by_service(self, records=None):
        """Generate report of occurrences grouped by service (CU-03)"""
        if records is None:
            records = [v for _, v in self.tree.get_all_records()]
        
        d = {}
        for r in records:
            s = getattr(r, 'service', None)
            if not s:
                continue
            d.setdefault(s, {'events': 0, 'errors': 0, 'last_error': None})
            d[s]['events'] += 1
            if r.calculate_level() == 'ERROR':
                d[s]['errors'] += 1
                if d[s]['last_error'] is None or r.timestamp > d[s]['last_error']:
                    d[s]['last_error'] = r.timestamp
        
        # Calculate error percentages and sort by error count
        for service in d:
            total = d[service]['events']
            errors = d[service]['errors']
            d[service]['error_percentage'] = (errors / total * 100) if total > 0 else 0
        
        # Sort by error count descending
        sorted_services = sorted(d.items(), key=lambda x: x[1]['errors'], reverse=True)
        
        return dict(sorted_services[:10])  # Return top 10
    
    def range_search(self, start_date, end_date, page=1, page_size=50):
        """Search records by date range with pagination (CU-02)"""
        try:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00')).isoformat()
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00')).isoformat()
        except ValueError:
            raise ValueError("Invalid date format. Use ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)")
        
        results = self.tree.range_search(start, end)
        
        if not results:
            return [], 0
        
        # Pagination
        total = len(results)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        paginated_results = results[start_idx:end_idx]
        
        return paginated_results, total
    
    def daily_control_break(self):
        """Generate daily control break report (CU-04)"""
        records = [(k, v) for k, v in self.tree.get_all_records()]
        
        if not records:
            return "No records found"
        
        # Group by date
        daily_data = defaultdict(lambda: {'total': 0, 'origins': defaultdict(int)})
        
        for timestamp, record in records:
            # Extract date part (YYYY-MM-DD)
            date = timestamp[:10]
            daily_data[date]['total'] += 1
            daily_data[date]['origins'][record.origin] += 1
        
        # Sort by date
        sorted_dates = sorted(daily_data.keys())
        
        # Build report
        report_lines = ["=== Corte de Control por Día ==="]
        total_general = 0
        
        for date in sorted_dates:
            data = daily_data[date]
            report_lines.append(f"--- {date} ---")
            report_lines.append(f"Registros: {data['total']}")
            
            # Build origin breakdown
            origins = data['origins']
            breakdown = ", ".join([f"{k}={v}" for k, v in sorted(origins.items())])
            report_lines.append(f"Desglose: {breakdown}")
            
            total_general += data['total']
        
        report_lines.append("=" * 32)
        report_lines.append(f"TOTAL GENERAL: {total_general} registros")
        
        return "\n".join(report_lines)
    
    def detect_recurrent_errors(self):
        """Detect and report recurrent errors (CU-06)"""
        records = [v for _, v in self.tree.get_all_records()]
        
        # Filter only error records
        error_records = []
        for r in records:
            if r.calculate_level() == 'ERROR':
                error_records.append(r)
        
        if not error_records:
            return "No error records found"
        
        # Normalize error messages
        error_groups = defaultdict(lambda: {
            'count': 0,
            'first_occurrence': None,
            'last_occurrence': None,
            'services': set()
        })
        
        for record in error_records:
            message = getattr(record, 'message', '')
            if not message:
                continue
            
            # Normalize message: remove timestamps, IDs, trace_ids
            normalized = self._normalize_error_message(message)
            
            group = error_groups[normalized]
            group['count'] += 1
            
            if group['first_occurrence'] is None or record.timestamp < group['first_occurrence']:
                group['first_occurrence'] = record.timestamp
            
            if group['last_occurrence'] is None or record.timestamp > group['last_occurrence']:
                group['last_occurrence'] = record.timestamp
            
            service = getattr(record, 'service', 'unknown')
            group['services'].add(service)
        
        # Sort by occurrence count
        sorted_errors = sorted(error_groups.items(), key=lambda x: x[1]['count'], reverse=True)
        
        # Build report
        report_lines = ["=== Top 5 Errores Recurrentes ==="]
        
        for i, (normalized_msg, data) in enumerate(sorted_errors[:5], 1):
            report_lines.append(f"{i}. \"{normalized_msg}\"")
            report_lines.append(f"Ocurrencias: {data['count']}")
            report_lines.append(f"Primera: {data['first_occurrence']}")
            report_lines.append(f"Última:   {data['last_occurrence']}")
            report_lines.append(f"Servicios: {', '.join(sorted(data['services']))}")
            report_lines.append("")
        
        return "\n".join(report_lines)
    
    def _normalize_error_message(self, message):
        """Normalize error message by removing variable parts"""
        # Remove timestamps
        normalized = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})', '[TIMESTAMP]', message)
        
        # Remove numeric IDs
        normalized = re.sub(r'\b\d+\b', '[ID]', normalized)
        
        # Remove trace_ids, session_ids, etc.
        normalized = re.sub(r'trace_id=\S+', 'trace_id=[ID]', normalized)
        normalized = re.sub(r'session_id=\S+', 'session_id=[ID]', normalized)
        normalized = re.sub(r'user_\d+', 'user_[ID]', normalized)
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def export_to_csv(self, records, filename):
        """Export records to CSV file"""
        import csv
        
        if not records:
            return False
        
        # Get all possible fields from records
        fieldnames = ['timestamp', 'origin']
        for record in records:
            for attr in dir(record):
                if not attr.startswith('_') and not callable(getattr(record, attr)):
                    if attr not in fieldnames:
                        fieldnames.append(attr)
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for record in records:
                row = {}
                for field in fieldnames:
                    value = getattr(record, field, '')
                    row[field] = value if value is not None else ''
                writer.writerow(row)
        
        return True
