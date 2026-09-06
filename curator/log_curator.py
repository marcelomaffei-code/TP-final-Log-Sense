from datetime import datetime
from exceptions.custom_exceptions import InvalidTimestampError, DuplicateEntryError

class LogCurator:
    def __init__(self):
        self._seen_records = set()  # For duplicate detection
        self._service_normalization_map = {
            'api-v1': 'api',
            'API_V1': 'api',
            'Api V1': 'api',
            'api_v2': 'api',
            'API_V2': 'api',
            'auth-service': 'auth-service',
            'auth_service': 'auth-service',
            'AUTH_SERVICE': 'auth-service',
            'payment-gateway': 'payment-gateway',
            'payment_gateway': 'payment-gateway',
            'PAYMENT_GATEWAY': 'payment-gateway',
            'user-service': 'user-service',
            'user_service': 'user-service',
            'USER_SERVICE': 'user-service',
        }
    
    def normalize_timestamp(self, ts):
        """Normalize timestamp to ISO 8601 format"""
        try:
            if ts.endswith('Z'):
                ts = ts[:-1] + '+00:00'
            dt = datetime.fromisoformat(ts)
            return dt.isoformat()
        except ValueError:
            raise InvalidTimestampError(f"Invalid timestamp format: {ts}")
    
    def normalize_service_name(self, service_name):
        """Normalize service name to canonical form"""
        if not service_name:
            return service_name
        
        # Remove extra whitespace
        service_name = service_name.strip()
        
        # Apply normalization map
        return self._service_normalization_map.get(service_name, service_name.lower())
    
    def clean_text(self, text):
        """Remove redundant whitespace and normalize case for standard fields"""
        if not text:
            return text
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def validate_record(self, record):
        """Validate that record has required fields"""
        if not record.timestamp:
            raise InvalidTimestampError("Record must have a timestamp")
        
        if not record.origin:
            raise ValueError("Record must have an origin")
        
        # Type-specific validation
        if record.origin == 'browser':
            if not hasattr(record, 'browser') or not record.browser:
                raise ValueError("Browser log must have browser field")
            if not hasattr(record, 'endpoint') or not record.endpoint:
                raise ValueError("Browser log must have endpoint field")
        
        elif record.origin == 'api':
            if not hasattr(record, 'service') or not record.service:
                raise ValueError("API log must have service field")
            if not hasattr(record, 'endpoint') or not record.endpoint:
                raise ValueError("API log must have endpoint field")
        
        elif record.origin == 'alert':
            if not hasattr(record, 'service') or not record.service:
                raise ValueError("Alert log must have service field")
            if not hasattr(record, 'severity') or not record.severity:
                raise ValueError("Alert log must have severity field")
        
        elif record.origin == 'audit':
            if not hasattr(record, 'user') or not record.user:
                raise ValueError("Audit log must have user field")
            if not hasattr(record, 'action') or not record.action:
                raise ValueError("Audit log must have action field")
    
    def check_duplicate(self, record):
        """Check if record is a duplicate (same timestamp + origin + message)"""
        # Create a unique key for duplicate detection
        message = getattr(record, 'message', '')
        if not message:
            # For records without message, use other identifying fields
            if record.origin == 'browser':
                message = f"{getattr(record, 'endpoint', '')}{getattr(record, 'session_id', '')}"
            elif record.origin == 'api':
                message = f"{getattr(record, 'endpoint', '')}{getattr(record, 'trace_id', '')}"
            elif record.origin == 'alert':
                message = f"{getattr(record, 'host', '')}"
            elif record.origin == 'audit':
                message = f"{getattr(record, 'target', '')}{getattr(record, 'ip', '')}"
        
        unique_key = (record.timestamp, record.origin, message)
        
        if unique_key in self._seen_records:
            raise DuplicateEntryError(f"Duplicate record: {unique_key}")
        
        self._seen_records.add(unique_key)
    
    def curate(self, record):
        """Apply all curation steps to a record"""
        # Normalize timestamp
        record._timestamp = self.normalize_timestamp(record.timestamp)
        
        # Normalize service name if applicable
        if hasattr(record, 'service') and record.service:
            record.service = self.normalize_service_name(record.service)
        
        # Clean text fields
        if hasattr(record, 'message') and record.message:
            record.message = self.clean_text(record.message)
        
        if hasattr(record, 'browser') and record.browser:
            record.browser = self.clean_text(record.browser)
        
        # Validate record
        self.validate_record(record)
        
        # Check for duplicates
        self.check_duplicate(record)
        
        return record
    
    def reset_duplicate_tracking(self):
        """Reset the duplicate tracking set (useful for new batches)"""
        self._seen_records.clear()
