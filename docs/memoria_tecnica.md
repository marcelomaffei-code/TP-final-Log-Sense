# Log Sense - Memoria tecnica

## 1. Introduccion

Log Sense centraliza registros de navegador, API, alertas y auditoria. El problema principal es que cada origen utiliza un formato diferente y la informacion queda dispersa. La solucion separa el procesamiento en cuatro etapas: parseo, curacion, almacenamiento ordenado y generacion de reportes.

El sistema no utiliza una base de datos tradicional. El indice principal es un Arbol B+ implementado en `storage/bplus_tree.py`, con hojas enlazadas y persistencia binaria mediante `pickle`.

## 2. Arquitectura

El flujo principal es:

1. `LogParser` identifica el formato y construye un objeto de dominio.
2. `LogCurator` normaliza timestamps, servicios y textos; valida campos y detecta duplicados.
3. `BPlusTree` inserta el registro usando una clave compuesta por timestamp e identidad del registro.
4. `ReportService` realiza busquedas temporales y genera agregaciones.
5. `PersistenceManager` guarda y recupera el arbol.

Las clases `BrowserLog`, `ApiLog`, `AlertLog` y `AuditLog` heredan de `LogRecord`. El metodo `calculate_level()` se resuelve polimorficamente segun el tipo de registro.

## 3. Modelo de dominio y POO

`LogRecord` es una clase abstracta con los atributos protegidos `_timestamp` y `_origin`, expuestos mediante properties. Las subclases agregan los datos especificos de cada origen.

- **Herencia:** las cuatro clases concretas reutilizan la identidad comun de `LogRecord`.
- **Polimorfismo:** API y browser calculan el nivel a partir de `status_code`; alertas traducen severidades; auditoria devuelve `INFO`.
- **Encapsulamiento:** timestamp y origen se consultan mediante properties; la curacion modifica el timestamp normalizado dentro del dominio.
- **Composicion:** `BPlusTree` crea y organiza sus `BPlusNode`; los nodos no tienen sentido fuera del arbol.
- **Asociacion:** parser, curador, reportes y persistencia colaboran con el arbol, pero tienen ciclo de vida independiente.
- **Cohesion:** cada modulo mantiene una responsabilidad especifica y el acoplamiento se limita a las interfaces publicas.

## 4. Arbol B+

Se eligio un B+ porque mantiene todos los valores en hojas enlazadas y permite localizar la hoja inicial en `O(log n)` para luego recorrer secuencialmente el intervalo. Los nodos internos contienen separadores; las hojas contienen claves y registros.

El orden usado por la aplicacion es 4 para las pruebas funcionales. La implementacion realiza split de hojas e internos cuando se alcanza el limite. La clave interna es `(timestamp, identidad)`, donde la identidad combina el origen y el mensaje o atributos identificadores. De esta manera, dos registros distintos pueden compartir timestamp sin sobrescribirse.

Complejidad esperada:

- Insercion: `O(log n)`.
- Busqueda exacta: `O(log n)` para localizar la hoja.
- Busqueda por rango: `O(log n + k)`, donde `k` es la cantidad de resultados.
- Recorrido completo: `O(n)`.

Una lista ordenada tendria inserciones `O(n)` por desplazamiento. Una tabla hash ofrece busqueda exacta promedio, pero no conserva orden ni resuelve rangos eficientemente.

## 5. Parseo y curacion

Los formatos se identifican mediante expresiones regulares. La curacion convierte timestamps a UTC con formato `YYYY-MM-DDTHH:MM:SSZ`, normaliza nombres de servicio, limpia espacios y valida campos obligatorios.

La deduplicacion utiliza `(timestamp, origen, mensaje)`; para registros sin mensaje usa atributos identificadores como endpoint/session, endpoint/trace, host o target/ip. Al iniciar con un arbol persistido, esos registros se registran nuevamente en el curador para evitar duplicados entre ejecuciones.

## 6. Persistencia

`PersistenceManager.save()` serializa el arbol a `logsense.db`. `load()` reconstruye el objeto completo. Si el archivo no puede leerse, se lanza `StorageCorruptionError`; `LogSense` respalda el archivo corrupto y comienza con un arbol nuevo.

La persistencia actual usa `pickle`, adecuado para este trabajo academico y para objetos Python controlados. En un sistema productivo deberia agregarse validacion de esquema, checksum y un formato de serializacion controlado.

## 7. Casos de uso y reportes

- **CU-01:** ingesta de archivos mixtos, con conteo de ingresados, duplicados y errores.
- **CU-02:** busqueda temporal inclusiva, paginada en 50 resultados, con exportacion CSV.
- **CU-03:** top 10 de servicios, eventos, errores, porcentaje y ultimo error.
- **CU-04:** corte diario con total y desglose por origen.
- **CU-05:** guardado y recuperacion del arbol.
- **CU-06:** top 5 de mensajes de error normalizados, fechas y servicios afectados.

Las alertas de severidad alta se consideran errores, igual que respuestas API o browser con estado mayor o igual a 500.

## 8. Pruebas y resultados

La suite funcional procesa los cuatro archivos de ejemplo y verifica los seis casos de uso. La prueba de carga se ejecuta con `python load_test.py`.

| Registros | Insercion (s) | Busqueda de rango (s) |
|---:|---:|---:|
| 1.000 | 0.0115 | 0.000158 |
| 10.000 | 0.2238 | 0.000147 |
| 50.000 | 0.9097 | 0.000184 |
| 100.000 | 1.3519 | 0.000186 |

Los valores fueron obtenidos en el equipo de desarrollo y deben repetirse en la instancia EC2 para el informe final.

## 9. Despliegue

En Ubuntu 20.04+ o Amazon Linux:

```bash
chmod +x install.sh start_service.sh
./install.sh
./start_service.sh
```

La instancia sugerida es `t3.micro` o `t2.micro`. Como la aplicacion es CLI, solo se requiere SSH por el puerto 22 restringido a la IP del operador.

## 10. Limitaciones y trabajo futuro

La eliminacion de registros es opcional y no esta implementada. La persistencia no incluye checksum ni migraciones de version. Para un entorno productivo se recomienda reemplazar `pickle` por un formato validado, agregar pruebas automatizadas formales y registrar metricas historicas de carga.

## 11. Referencias

Canning, J., Broder, A., & Lafore, R. (2022). *Data Structures & Algorithms in Python*. Addison-Wesley Professional.

Fowler, M. (2004). *UML distilled: A brief guide to the standard object modeling language*. Addison-Wesley Professional.

Martin, R. C. (2012). *Codigo limpio: Manual de estilo para el desarrollo agil de software*.

Python Software Foundation. (s. f.). *Python documentation*. https://docs.python.org/3/

VisuAlgo. (s. f.). *Visualising data structures and algorithms*. https://visualgo.net/en
