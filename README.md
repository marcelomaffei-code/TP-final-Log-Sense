# LogSense - Sistema de Observación y Análisis de Registros Tecnológicos

Sistema de observabilidad desarrollado para MetaX S.A. que centraliza, procesa y analiza logs de múltiples fuentes (navegador, API, alertas del sistema, auditoría) utilizando un motor de almacenamiento basado en Árbol B+ implementado desde cero.

## Características

- **Motor de almacenamiento B+ Tree**: Implementación desde cero con persistencia en disco
- **Parser multi-formato**: Soporte para logs de navegador, API, alertas y auditoría
- **Curación de datos**: Normalización de timestamps, servicios, eliminación de duplicados
- **Reportes analíticos**: Búsqueda por rango temporal, ocurrencias por servicio, cortes de control, errores recurrentes
- **Persistencia**: Guardado y recuperación automática del estado del árbol
- **Estructuras auxiliares**: Queue, Stack, Set y Dictionary implementados desde cero

## Estructura del Proyecto

```
TP-final-Log-Sense/
├── domain/                 # Modelos de dominio (POO)
│   ├── log_record.py      # Clase base abstracta
│   ├── browser_log.py     # Logs de navegador
│   ├── api_log.py         # Logs de API
│   ├── alert_log.py       # Logs de alertas
│   └── audit_log.py      # Logs de auditoría
├── storage/               # Motor de almacenamiento
│   ├── bplus_tree.py      # Árbol B+ implementado desde cero
│   ├── node.py            # Nodo del árbol B+
│   └── persistence.py     # Gestión de persistencia
├── parser/                # Parser de logs
│   └── log_parser.py      # Parser con regex para 4 formatos
├── curator/               # Curación de datos
│   └── log_curator.py     # Normalización y validación
├── reports/               # Servicio de reportes
│   └── report_service.py  # Generación de reportes analíticos
├── structures/            # Estructuras auxiliares desde cero
│   ├── queue.py           # Cola FIFO
│   ├── stack.py           # Pila LIFO
│   ├── custom_set.py      # Set con hash table
│   └── custom_dict.py     # Dictionary con hash table
├── exceptions/            # Excepciones personalizadas
│   └── custom_exceptions.py
├── main.py                # Aplicación principal con menú interactivo
├── install.sh             # Script de instalación para AWS
├── start_service.sh       # Script de inicio para AWS
├── logs_browser.txt       # Archivo de prueba (logs navegador)
├── logs_api.txt           # Archivo de prueba (logs API)
├── logs_alertas.txt       # Archivo de prueba (logs alertas)
├── logs_audit.txt         # Archivo de prueba (logs auditoría)
└── README.md              # Este archivo
```

## Requisitos

- Python 3.7+
- No requiere dependencias externas (todas las estructuras están implementadas desde cero)

## Instalación y Ejecución Local

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd TP-final-Log-Sense
```

### 2. Ejecutar la aplicación
```bash
python main.py
```

### 3. Usar el menú interactivo

El sistema mostrará un menú con las siguientes opciones:

1. **Ingestar registros desde archivo (CU-01)**
   - Procesa archivos con logs en formatos mixtos
   - Parsea, cura y valida cada registro
   - Reporta: total ingresado, descartado y con errores

2. **Buscar registros por rango temporal (CU-02)**
   - Busca registros entre dos fechas (formato ISO 8601)
   - Paginación de resultados (50 por página)
   - Opción de exportar a CSV

3. **Reporte de ocurrencias por servicio (CU-03)**
   - Muestra Top 10 servicios con más errores
   - Incluye: total eventos, total errores, % fallos, último error

4. **Corte de control por día (CU-04)**
   - Listado cronológico con subtotales por día
   - Desglose por origen (browser, api, alerta, auditoría)

5. **Detectar errores recurrentes (CU-06)**
   - Normaliza mensajes de error
   - Muestra Top 5 errores más frecuentes
   - Incluye fechas de primera/última ocurrencia y servicios afectados

6. **Mostrar estadísticas**
   - Total de registros en el árbol
   - Estado del archivo de persistencia

7. **Guardar estado y salir**
   - Persiste el árbol en disco (logsense.db)

0. **Salir sin guardar**

## Formatos de Logs Soportados

### Browser Log
```
[2025-09-15T14:32:01Z] BROWSER | chrome/120.0 | GET /api/products?page=2 | 200 | 145ms | session_id=a8f3k2
```

### API Log
```
[2025-09-15T14:35:22Z] API | service=auth-service | POST /login | 500 | 3200ms | trace_id=xyz789 | msg="Database connection timeout"
```

### Alert Log
```
[2025-09-15T14:40:00Z] ALERT | service=payment-gateway | severity=high | msg="Retry queue exceeded 1000 pending items" | host=prod-node-03
```

### Audit Log
```
[2025-09-15T15:00:11Z] AUDIT | user=admin@mplataforma.com | action=DELETE_USER | target=user_4521 | ip=190.50.32.10
```

## Despliegue en AWS EC2

### 1. Crear instancia EC2

1. Iniciar sesión en AWS Console
2. Ir a EC2 → Launch Instance
3. Seleccionar:
   - **AMI**: Ubuntu Server 20.04 LTS o Amazon Linux 2
   - **Instance Type**: t2.micro o t3.micro (para pruebas)
   - **Key Pair**: Crear o seleccionar una clave SSH existente
4. Configurar Security Group:
   - SSH (Port 22): Tu IP
   - No requiere puertos adicionales (aplicación CLI)
5. Lanzar instancia

### 2. Conectarse a la instancia

```bash
ssh -i tu-clave.pem ec2-user@<public-ip>
# o para Ubuntu:
ssh -i tu-clave.pem ubuntu@<public-ip>
```

### 3. Instalar dependencias

```bash
# Dar permisos de ejecución a los scripts
chmod +x install.sh start_service.sh

# Ejecutar script de instalación
./install.sh
```

### 4. Transferir archivos

Opción 1: Usar SCP
```bash
scp -i tu-clave.pem -r TP-final-Log-Sense ec2-user@<public-ip>:~
```

Opción 2: Usar Git en EC2
```bash
git clone <repository-url>
cd TP-final-Log-Sense
./install.sh
```

### 5. Iniciar la aplicación

```bash
./start_service.sh
```

### 6. Prueba de Carga

Para realizar la prueba de carga con 50,000 registros:

```bash
# Generar archivo de prueba grande
python generate_test_data.py 50000

# Ingestar el archivo
python main.py
# Seleccionar opción 1 e ingresar el archivo generado
```

## Archivos Generados

- `logsense.db`: Archivo de persistencia del árbol B+
- `logs_errores.txt`: Registro de líneas con errores de parseo
- `export_YYYYMMDD_HHMMSS.csv`: Exportaciones CSV de búsquedas

## Casos de Uso Implementados

- **CU-01**: Ingestar lote de registros desde archivo
- **CU-02**: Buscar registros por rango temporal
- **CU-03**: Generar reporte de ocurrencias por servicio
- **CU-04**: Generar corte de control por día
- **CU-05**: Persistir y recuperar estado del árbol
- **CU-06**: Detectar errores recurrentes

## Diseño POO

### Principios Aplicados

- **Herencia**: Jerarquía de clases con `LogRecord` como base abstracta
- **Polimorfismo**: Método `calculate_level()` implementado diferente en cada subclase
- **Encapsulamiento**: Atributos privados con acceso via properties
- **Composición**: BPlusTree compuesto por BPlusNode
- **Cohesión**: Cada clase tiene responsabilidad única y clara
- **Bajo acoplamiento**: Mínimas dependencias entre módulos

## Justificación del Árbol B+

Se eligió **Árbol B+** sobre alternativas por:

- **Búsqueda eficiente**: O(log n) para inserción y búsqueda
- **Búsqueda por rango**: Las hojas enlazadas permiten recorrido secuencial eficiente
- **Ordenamiento natural**: Los datos se mantienen ordenados por timestamp automáticamente
- **Persistencia**: Estructura fácil de serializar y recuperar
- **Uso real**: Es la estructura usada por bases de datos reales para índices

Comparación con alternativas:
- **Lista ordenada**: Inserción O(n), muy lento para millones de registros
- **Hash table**: No mantiene orden, no soporta búsqueda por rango eficientemente

## Licencia

Proyecto académico para TP Final de Sistemas.

