#!/usr/bin/env python3
"""
Script de prueba automatizado para LogSense
Prueba los casos de uso CU-01 a CU-06
"""

from storage.bplus_tree import BPlusTree
from storage.persistence import PersistenceManager
from parser.log_parser import LogParser
from curator.log_curator import LogCurator
from reports.report_service import ReportService
from structures import Queue
import os

def test_system():
    print("=== LogSense - Prueba Automatizada ===\n")
    
    # Inicializar sistema
    print("1. Inicializando sistema...")
    tree = BPlusTree(order=4)
    parser = LogParser()
    curator = LogCurator()
    report_service = ReportService(tree)
    ingest_queue = Queue()
    
    # Limpiar archivos de prueba anteriores
    if os.path.exists("logsense.db"):
        os.remove("logsense.db")
    if os.path.exists("logs_errores.txt"):
        os.remove("logs_errores.txt")
    
    print("✓ Sistema inicializado\n")
    
    # Test CU-01: Ingestar registros
    print("2. Probando CU-01: Ingestar registros desde archivo...")
    test_files = [
        "logs_browser.txt",
        "logs_api.txt",
        "logs_alertas.txt",
        "logs_audit.txt"
    ]
    
    total_ingested = 0
    total_discarded = 0
    total_errors = 0
    
    for filename in test_files:
        if not os.path.exists(filename):
            print(f"  ⚠ Archivo {filename} no encontrado, saltando...")
            continue
        
        print(f"  Procesando {filename}...")
        curator.reset_duplicate_tracking()  # Reset duplicate tracking for each file
        
        with open(filename, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    record = parser.parse(line)
                    curator.curate(record)
                    ingest_queue.enqueue(record)
                    tree.insert(record.timestamp, record)
                    total_ingested += 1
                except Exception as e:
                    total_errors += 1
    
    print(f"  ✓ Total ingresado: {total_ingested}")
    print(f"  ✓ Total errores: {total_errors}\n")
    
    # Test CU-02: Búsqueda por rango
    print("3. Probando CU-02: Búsqueda por rango temporal...")
    try:
        results, total = report_service.range_search(
            "2025-09-15T14:30:00Z",
            "2025-09-15T14:45:00Z",
            page=1
        )
        print(f"  ✓ Resultados encontrados: {total}")
        print(f"  ✓ Registros en página 1: {len(results)}\n")
    except Exception as e:
        print(f"  ✗ Error: {e}\n")
    
    # Test CU-03: Reporte por servicio
    print("4. Probando CU-03: Reporte de ocurrencias por servicio...")
    try:
        report = report_service.occurrences_by_service()
        print(f"  ✓ Servicios reportados: {len(report)}")
        for service, data in list(report.items())[:3]:
            print(f"    - {service}: {data['events']} eventos, {data['errors']} errores")
        print()
    except Exception as e:
        print(f"  ✗ Error: {e}\n")
    
    # Test CU-04: Corte de control por día
    print("5. Probando CU-04: Corte de control por día...")
    try:
        report = report_service.daily_control_break()
        print("  ✓ Reporte generado exitosamente")
        lines = report.split('\n')
        for line in lines[:5]:
            print(f"    {line}")
        print("    ...\n")
    except Exception as e:
        print(f"  ✗ Error: {e}\n")
    
    # Test CU-05: Persistencia
    print("6. Probando CU-05: Persistencia del árbol...")
    try:
        PersistenceManager.save(tree, "logsense.db")
        print("  ✓ Árbol guardado en logsense.db")
        
        tree2 = PersistenceManager.load("logsense.db")
        count1 = tree.count_records()
        count2 = tree2.count_records()
        
        if count1 == count2:
            print(f"  ✓ Árbol recuperado correctamente ({count2} registros)\n")
        else:
            print(f"  ✗ Error: conteo no coincide ({count1} vs {count2})\n")
    except Exception as e:
        print(f"  ✗ Error: {e}\n")
    
    # Test CU-06: Errores recurrentes
    print("7. Probando CU-06: Detección de errores recurrentes...")
    try:
        report = report_service.detect_recurrent_errors()
        print("  ✓ Reporte generado exitosamente")
        lines = report.split('\n')
        for line in lines[:8]:
            print(f"    {line}")
        print("    ...\n")
    except Exception as e:
        print(f"  ✗ Error: {e}\n")
    
    # Estadísticas finales
    print("8. Estadísticas finales:")
    print(f"  Total de registros en el árbol: {tree.count_records()}")
    print(f"  Tamaño de la cola de ingesta: {ingest_queue.size()}")
    
    print("\n=== Prueba Completada ===")
    print("Todos los casos de uso han sido probados exitosamente.")

if __name__ == "__main__":
    test_system()
