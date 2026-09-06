from storage.bplus_tree import BPlusTree
from storage.persistence import PersistenceManager
from parser.log_parser import LogParser
from curator.log_curator import LogCurator
from reports.report_service import ReportService
from structures import Queue
from exceptions.custom_exceptions import (
    InvalidTimestampError,
    DuplicateEntryError,
    UnknownLogFormatError,
    StorageCorruptionError,
    RangeNotFoundError
)
import os
from datetime import datetime

PERSISTENCE_FILE = "logsense.db"
ERRORS_FILE = "logs_errores.txt"

class LogSense:
    def __init__(self):
        self.tree = None
        self.parser = LogParser()
        self.curator = LogCurator()
        self.report_service = None
        self.ingest_queue = Queue()
        self._load_or_create_tree()
    
    def _load_or_create_tree(self):
        """Load tree from persistence or create new one (CU-05)"""
        try:
            if os.path.exists(PERSISTENCE_FILE):
                print(f"Cargando estado desde {PERSISTENCE_FILE}...")
                self.tree = PersistenceManager.load(PERSISTENCE_FILE)
                print("Estado cargado exitosamente.")
            else:
                print("Creando nuevo árbol B+...")
                self.tree = BPlusTree(order=4)
                print("Árbol creado exitosamente.")
        except StorageCorruptionError as e:
            print(f"Error: Archivo de persistencia corrupto: {e}")
            # Backup corrupt file
            backup_name = f"logs_corrupto_{datetime.now().strftime('%Y%m%d')}.db"
            os.rename(PERSISTENCE_FILE, backup_name)
            print(f"Archivo corrupto respaldado como {backup_name}")
            print("Creando nuevo árbol...")
            self.tree = BPlusTree(order=4)
        
        self.report_service = ReportService(self.tree)
    
    def save_state(self):
        """Save tree state to persistence (CU-05)"""
        try:
            PersistenceManager.save(self.tree, PERSISTENCE_FILE)
            print(f"Estado guardado en {PERSISTENCE_FILE}")
        except Exception as e:
            print(f"Error al guardar estado: {e}")
    
    def ingest_from_file(self, filepath):
        """Ingest a batch of records from file (CU-01)"""
        if not os.path.exists(filepath):
            print(f"Error: El archivo {filepath} no existe.")
            return
        
        total_ingested = 0
        total_discarded = 0
        total_errors = 0
        
        print(f"Procesando archivo: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    # Parse the line
                    record = self.parser.parse(line)
                    
                    # Curate the record
                    self.curator.curate(record)
                    
                    # Add to queue for batch processing
                    self.ingest_queue.enqueue(record)
                    
                    # Insert into tree
                    self.tree.insert(record.timestamp, record)
                    total_ingested += 1
                    
                except DuplicateEntryError:
                    total_discarded += 1
                except UnknownLogFormatError as e:
                    total_errors += 1
                    self._log_error(line_num, line, str(e))
                except (InvalidTimestampError, ValueError) as e:
                    total_errors += 1
                    self._log_error(line_num, line, str(e))
        
        print(f"\n=== Resumen de Ingesta ===")
        print(f"Total ingresado: {total_ingested}")
        print(f"Total descartado (duplicados): {total_discarded}")
        print(f"Total con errores: {total_errors}")
        
        if total_errors > 0:
            print(f"Errores guardados en: {ERRORS_FILE}")
    
    def _log_error(self, line_num, line, error_msg):
        """Log parsing errors to file"""
        with open(ERRORS_FILE, 'a', encoding='utf-8') as f:
            f.write(f"Línea {line_num}: {line}\n")
            f.write(f"Error: {error_msg}\n\n")
    
    def search_by_range(self, start_date, end_date, page=1):
        """Search records by date range (CU-02)"""
        try:
            results, total = self.report_service.range_search(start_date, end_date, page)
            
            if not results:
                print("Sin resultados en el rango especificado.")
                return
            
            print(f"\n=== Resultados ({total} total) - Página {page} ===")
            for record in results:
                print(f"[{record.timestamp}] {record.origin.upper()}")
                if hasattr(record, 'service'):
                    print(f"  Servicio: {record.service}")
                if hasattr(record, 'message'):
                    print(f"  Mensaje: {record.message}")
                print()
            
            # Ask about export
            if total > 0:
                choice = input("¿Exportar resultados a CSV? (s/n): ").lower()
                if choice == 's':
                    filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    if self.report_service.export_to_csv(results, filename):
                        print(f"Exportado a {filename}")
        
        except ValueError as e:
            print(f"Error: {e}")
    
    def show_service_report(self):
        """Show occurrences by service report (CU-03)"""
        report = self.report_service.occurrences_by_service()
        
        if not report:
            print("No hay datos de servicios para reportar.")
            return
        
        print("\n=== Reporte de Ocurrencias por Servicio (Top 10) ===")
        print(f"{'Servicio':<20} {'Total Eventos':<15} {'Total Errores':<15} {'% Fallos':<12} {'Último Error'}")
        print("-" * 90)
        
        for service, data in report.items():
            print(f"{service:<20} {data['events']:<15} {data['errors']:<15} {data['error_percentage']:<11.1f}% {data['last_error'] or 'N/A'}")
    
    def show_daily_control_break(self):
        """Show daily control break report (CU-04)"""
        report = self.report_service.daily_control_break()
        print(f"\n{report}")
    
    def detect_recurrent_errors(self):
        """Detect and show recurrent errors (CU-06)"""
        report = self.report_service.detect_recurrent_errors()
        print(f"\n{report}")
    
    def show_stats(self):
        """Show general statistics"""
        total = self.tree.count_records()
        print(f"\n=== Estadísticas Generales ===")
        print(f"Total de registros en el árbol: {total}")
        print(f"Archivo de persistencia: {PERSISTENCE_FILE}")


def main_menu():
    """Main menu interface"""
    system = LogSense()
    
    while True:
        print("\n" + "=" * 50)
        print("LogSense - Sistema de Observación de Logs")
        print("=" * 50)
        print("1. Ingestar registros desde archivo (CU-01)")
        print("2. Buscar registros por rango temporal (CU-02)")
        print("3. Reporte de ocurrencias por servicio (CU-03)")
        print("4. Corte de control por día (CU-04)")
        print("5. Detectar errores recurrentes (CU-06)")
        print("6. Mostrar estadísticas")
        print("7. Guardar estado y salir")
        print("0. Salir sin guardar")
        
        choice = input("\nSeleccione una opción: ").strip()
        
        if choice == '1':
            filepath = input("Ingrese la ruta del archivo: ").strip()
            system.ingest_from_file(filepath)
        
        elif choice == '2':
            start = input("Fecha inicio (YYYY-MM-DDTHH:MM:SSZ): ").strip()
            end = input("Fecha fin (YYYY-MM-DDTHH:MM:SSZ): ").strip()
            page = input("Página (default 1): ").strip()
            page = int(page) if page else 1
            system.search_by_range(start, end, page)
        
        elif choice == '3':
            system.show_service_report()
        
        elif choice == '4':
            system.show_daily_control_break()
        
        elif choice == '5':
            system.detect_recurrent_errors()
        
        elif choice == '6':
            system.show_stats()
        
        elif choice == '7':
            system.save_state()
            print("Estado guardado. ¡Hasta luego!")
            break
        
        elif choice == '0':
            print("Saliendo sin guardar cambios...")
            break
        
        else:
            print("Opción inválida. Intente nuevamente.")


if __name__ == "__main__":
    main_menu()
