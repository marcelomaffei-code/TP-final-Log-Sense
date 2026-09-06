TP final: Log Sense - sistema de 
observación y análisis de registros 
tecnológicos 
MetaX S.A. es una empresa tecnológica en plena expansión que ofrece múltiples servicios 
digitales: un portal web de comercio electrónico, una API REST para integradores externos, 
una aplicación móvil para clientes finales y un panel administrativo interno. Actualmente la 
empresa tiene un volumen creciente de datos dispersos en múltiples sistemas 
heterogéneos. 
Desde hace meses, el equipo de operaciones viene notando que los incidentes se detectan 
tarde. Los clientes se quejan en redes sociales antes de que el equipo interno se entere de 
que algo falló. Cuando alguien del equipo de Infraestructura intenta investigar qué pasó, 
descubre que: 
● Los logs del navegador de los usuarios están dispersos en archivos de texto plano 
sin ningún orden. 
● Los mensajes de alerta que envían los servicios llegan por múltiples canales (email, 
webhook, colas de mensajes) y nadie los centraliza. 
● Las métricas de respuesta de la API están en un formato distinto al de las alertas del 
sistema operativo. 
● Los registros de auditoría del panel administrativo se guardan en CSV que nadie 
revisa hasta que hay un problema. 
● Cada sistema usa su propio formato de fecha, sus propios niveles de severidad y sus 
propias convenciones de nombres. 
La directiva ha tomado una decisión: se necesita construir un sistema interno de observación 
que centralice, ordene y permita consultar toda esta información. No quieren comprar una 
solución comercial porque necesitan entender cómo funciona internamente y, además, 
quieren que sea desplegable en su infraestructura de AWS. 
El equipo de arquitectura ha establecido una restricción clara: 
"No queremos una base de datos tradicional. Queremos que ustedes diseñen e 
implementen el motor de almacenamiento desde cero. Necesitamos que los registros estén 
ordenados temporalmente y que las búsquedas por rango de fecha sean eficientes incluso 
con millones de registros. Investiguen e implementen un Árbol B o B+." 
1 
El problema real: la metadata invisible. 
Lo que la empresa descubre es que el valor no está en el mensaje crudo del log, sino en la 
metadata que se puede extraer de él. Cada registro que ingresa contiene información oculta 
que, si se sabe extraer y organizar, permite responder preguntas críticas: 
Pregunta de Negocio 
Metadata a Extraer 
¿Qué servicio falló más esta semana? 
Nombre del servicio, nivel de 
severidad, fecha 
Origen del Dato 
Logs de API, alertas del 
sistema 
¿En qué franja horaria hay más 
errores? 
¿Un mismo error se repite 
sistemáticamente? 
¿Qué páginas web generan más 
errores de carga? 
¿Cuánto tarda la API en responder 
bajo carga? 
¿Hay patrones de alertas 
correlacionadas? 
Hora del evento, tipo de error 
Mensaje normalizado, conteo de 
ocurrencias 
URL, código HTTP, navegador 
Latencia, endpoint, timestamp 
Servicio origen, ventana temporal, 
frecuencia 
Todos los orígenes 
Cualquier fuente 
Browser logs 
API logs 
Alertas del sistema 
El sistema no debe simplemente "guardar texto". Debe procesar cada registro entrante, 
extraer atributos estructurados, normalizarlos y almacenarlos de forma que las consultas 
analíticas sean eficientes. 
Los orígenes de datos: qué ingresa al sistema. 
A continuación se describen los tipos de registros que el sistema debe poder recibir. Estos 
son ejemplos: 
Caso 1: registro de Navegador 
Un evento de navegador ingresa como una cadena de texto semi-estructurada: 
[2025-09-15T14:32:01Z] BROWSER | chrome/120.0 | GET /api/products?page=2 | 200 | 
145ms | session_id=a8f3k2 
Metadata esperada a extraer: 
● timestamp: 2025-09-15T14:32:01Z 
● origen: browser 
● navegador: chrome/120.0 
● método_http: GET 
● endpoint: /api/products 
2 
● status_code: 200 
● tiempo_respuesta_ms: 145 
● session_id: a8f3k2 
● nivel: derivado automáticamente (INFO si status < 400, WARN si 400-499, ERROR si 
≥ 500) 
Caso 2: registro de API 
[2025-09-15T14:35:22Z] API | service=auth-service | POST /login | 500 | 3200ms | 
trace_id=xyz789 | msg="Database connection timeout" 
Metadata esperada: 
● timestamp: 2025-09-15T14:35:22Z 
● origen: api 
● servicio: auth-service 
● método_http: POST 
● endpoint: /login 
● status_code: 500 
● latencia_ms: 3200 
● trace_id: xyz789 
● mensaje: "Database connection timeout" 
● nivel: ERROR (automático por status ≥ 500) 
Caso 3: alerta del Sistema 
[2025-09-15T14:40:00Z] ALERT | service=payment-gateway | severity=high | msg="Retry 
queue exceeded 1000 pending items" | host=prod-node-03 
Metadata esperada: 
● timestamp: 2025-09-15T14:40:00Z 
● origen: alerta 
● servicio: payment-gateway 
● severidad: alta 
● mensaje: "Retry queue exceeded 1000 pending items" 
● host: prod-node-03 
Caso 4: evento de Auditoría 
[2025-09-15T15:00:11Z] AUDIT | user=admin@mplataforma.com | action=DELETE_USER | 
target=user_4521 | ip=190.50.32.10 
3 
Metadata esperada: 
● timestamp: 2025-09-15T15:00:11Z 
● origen: auditoria 
● usuario: admin@mplataforma.com 
● accion: DELETE_USER 
● objetivo: user_4521 
● ip: 190.50.32.10 
¿Cómo viven los datos dentro del sistema? 
El flujo de vida de cada registro es el siguiente: 
Fase 1: preparación de datos 
● Ingesta (texto crudo): recepción inicial de los datos en su formato más crudo (texto, 
logs, etc.). 
● Parseo y extracción de metadata: identificación del tipo de registro, extracción de 
atributos clave y normalización inicial de los datos. 
● Validación y curación: verificación de la calidad de los datos, eliminación de 
duplicados y estandarización de nombres y formatos. 
Fase 2: modelado y almacenamiento 
● Construcción del objeto de dominio: creación de instancias de clases específicas 
para dar estructura a los datos. 
● Inserción en Árbol B/B+: ordenamiento de los objetos por timestamp y uso de una 
clave secundaria para garantizar la unicidad y la eficiencia de la búsqueda. 
● Persistencia en disco: serialización de los nodos del árbol y guardado de la 
estructura en un archivo físico. 
Fase 3: resultado final 
● Disponible para consultas y reportes: los datos están listos y optimizados para ser 
consultados rápidamente por sistemas de reporte y análisis. 
4 
Casos de uso 
CU-01: Ingestar un lote de registros desde archivo 
Actor: Operador del sistema precondición: Existe un archivo de texto con registros en 
formatos mixtos. Flujo principal: 
1. El operador indica la ruta del archivo a procesar. 
2. El sistema lee cada línea del archivo. 
3. Por cada línea, identifica el tipo de registro (browser, api, alerta, auditoría). 
4. Extrae la metadata correspondiente al tipo detectado. 
5. Valida que el registro sea correcto (fecha válida, campos obligatorios presentes). 
6. Si el registro es duplicado exacto (mismo timestamp + origen + mensaje), se 
descarta. 
7. El registro se inserta en el árbol B+ ordenado por timestamp. 
8. Al finalizar, el sistema reporta: total ingresado, total descartado, total con errores. 
Flujo alternativo: 
● Si una línea no coincide con ningún formato conocido, se registra en un archivo de 
errores (logs_errores.txt) con su número de línea, sin detener el proceso. 
CU-02: Buscar registros por rango temporal 
Actor: Analista de datos Precondición: El árbol B/B+ contiene registros persistidos. Flujo 
principal: 
1. El analista ingresa una fecha de inicio y una fecha de fin (formato ISO 8601). 
2. El sistema localiza en el árbol el primer nodo hoja que contiene la clave de inicio. 
3. Recorre las hojas enlazadas recolectando todos los registros hasta la fecha de fin. 
4. Los resultados se muestran paginados (ej. 50 por página). 
5. Se ofrece la opción de exportar el resultado a CSV. 
Flujo alternativo: 
● Si no hay registros en el rango, se informa "Sin resultados". 
CU-03: Generar reporte de ocurrencias por servicio 
Actor: Equipo de Operaciones Precondición: Existen registros de tipo API y Alerta en el 
sistema. Flujo principal: 
1. El analista solicita el reporte de ocurrencias agrupadas por servicio. 
2. El sistema recorre los registros (secuencialmente desde el árbol o desde un buffer en 
memoria). 
3. Agrupa por nombre de servicio. 
4. Cuenta: total de eventos, total de errores (status ≥ 400 o severidad alta), porcentaje 
de fallos. 
5. Ordena los servicios de mayor a menor cantidad de fallos. 
6. Presenta el Top 10 con los siguientes campos: 
5 
Servicio 
Total Eventos Total Errores 
% Fallos 
auth-service 
450 
89 
Último Error 
19.8% 
payment-gateway 
320 
45 
CU-04: Generar corte de control por día 
14.1% 
2025-09-15T14:35:22Z 
2025-09-15T14:40:00Z 
Actor: Analista de datos Precondición: Existen registros de al menos 2 días diferentes. Flujo 
principal: 
1. El analista solicita un listado cronológico completo con cortes de control por fecha. 
2. El sistema recorre el árbol en orden secuencial (in-order traversal de las hojas). 
3. Por cada cambio de fecha (día), imprime un corte con: 
○ Fecha del bloque. 
○ Cantidad de registros del día. 
○ Desglose por origen (browser: X, api: Y, alerta: Z, auditoría: W). 
4. Al final del listado, imprime un total general. 
Ejemplo de salida: 
=== Corte de Control por Día === --- 2025-09-15 --- 
Registros: 1,240 
Desglose: browser=620, api=340, alerta=180, auditoria=100 --- 2025-09-16 --- 
Registros: 980 
Desglose: browser=500, api=280, alerta=120, auditoria=80 
================================ 
TOTAL GENERAL: 2,220 registros 
CU-05: Persistir y recuperar el estado del árbol 
Actor: Sistema (automático) Precondición: Hay registros en memoria o en disco. Flujo 
principal: 
1. Al cerrar la aplicación, el sistema serializa todos los nodos del árbol al archivo de 
persistencia. 
2. Al iniciar la aplicación, el sistema lee el archivo y reconstruye el árbol en memoria. 
3. Si el archivo no existe, se crea un árbol vacío. 
6 
Flujo alternativo: 
● Si el archivo está corrupto, se lanza una excepción personalizada y se ofrece iniciar 
un árbol nuevo respaldando el corrupto como logs_corrupto_YYYYMMDD.db. 
CU-06: Detectar errores recurrentes 
Actor: Equipo de Operaciones Precondición: Existen registros de tipo API y Alerta. Flujo 
principal: 
1. El analista solicita el reporte de "errores recurrentes". 
2. El sistema normaliza los mensajes de error (elimina timestamps, IDs numéricos, 
trace_ids variables). 
3. Agrupa por mensaje normalizado. 
4. Cuenta ocurrencias y muestra el Top 5 de mensajes más frecuentes. 
5. Para cada uno, muestra: mensaje normalizado, primera ocurrencia, última 
ocurrencia, total de repeticiones, servicios afectados. 
Ejemplo: 
=== Top 5 Errores Recurrentes === 
1. "Database connection timeout" 
Ocurrencias: 47 
Primera: 2025-09-14T08:15:00Z 
Última:   2025-09-15T14:35:22Z 
Servicios: auth-service, user-service 
2. "Retry queue exceeded threshold" 
Ocurrencias: 23 
Primera: 2025-09-15T10:00:00Z 
Última:   2025-09-15T14:40:00Z 
Servicios: payment-gateway 
7 
Objetivos Generales 
Código Objetivo 
OG-01 
OG-02 
OG-03 
OG-04 
Modelar un dominio de problema real utilizando los 
principios de POO, aplicando herencia, polimorfismo, 
encapsulamiento, interfaces , composición y relaciones 
entre objetos. 
Implementar estructuras de datos complejas (Árbol B/B+) 
desde cero, comprendiendo su funcionamiento interno y 
justificando su elección frente a alternativas más simples. 
Diseñar e implementar un sistema de persistencia en 
disco que permita recuperar el estado completo del 
sistema tras un reinicio. 
Extraer, normalizar y validar metadata a partir de 
registros semi-estructurados, aplicando técnicas de 
curación de datos. 
OG-05 
OG-06 
OG-07 
Generar reportes analíticos utilizando cortes de control y 
agregaciones, aprovechando el ordenamiento natural del 
árbol. 
Documentar el sistema mediante diagramas UML 
(Clases, Casos de Uso, Secuencia) que reflejen fielmente 
la implementación. 
Desplegar la solución en una máquina virtual de AWS, 
demostrando capacidad de operar el sistema en un 
entorno real. 
8 
Requerimientos técnicos 
Módulo de persistencia: Árbol B/B+ (núcleo del desafío) 
Como parte del trabajo final deben implementar su propio motor de índices basado en Árbol 
B o B+ desde cero. No se permite el uso de bibliotecas externas que implementen esta 
estructura. Si pueden utilizar componentes que ayuden a alcanzarlo, pero ustedes deben ser 
el artífice de su implementación. 
Requisitos: 
1. Investigación obligatoria: el informe debe explicar cómo funciona un Árbol B/B+ 
(estructura de nodos, factor de ramificación, splitting y merging). Debe citar 
bibliografía de referencia. 
2. Implementación desde cero: Crear el árbol B/B+. 
3. Ordenamiento natural: los datos deben mantenerse ordenados por timestamp de 
forma ascendente. 
4. Persistencia en disco: los nodos del árbol deben guardarse en un archivo binario (.db 
o .dat) para que la información sobreviva al cierre del programa. 
5. Búsqueda por rango: el árbol debe soportar búsqueda de registros entre dos fechas, 
aprovechando el recorrido de hojas enlazadas (en caso de B+) o el recorrido in-order 
(en caso de B). 
6. Operaciones mínimas: inserción con split, búsqueda exacta, búsqueda por rango. La 
eliminación es opcional (bonus). 
Módulo de curación de datos 
El sistema debe incluir funciones de curación que se apliquen durante la ingesta: 
1. Normalización de fechas: convertir todos los timestamps a formato ISO 8601 
(YYYY-MM-DDTHH:MM:SSZ). 
2. Normalización de nombres de servicio: unificar variantes como api-v1, API_V1, Api 
V1 a un nombre canónico (API). 
3. Eliminación de duplicados: dos registros con el mismo timestamp + origen + mensaje 
se consideran duplicados y se descartan. 
4. Limpieza de texto: eliminar espacios en blanco redundantes, normalizar 
mayúsculas/minúsculas en campos estándar. 
5. Validación de campos obligatorios: todo registro debe tener al menos timestamp y 
origen. Los campos específicos de cada tipo deben validarse según corresponda. 
9 
Módulo de consultas y reportes 
1. Búsqueda por rango temporal: dadas dos fechas, retornar todos los registros en ese 
intervalo ordenados cronológicamente. Debe paginar los resultados (50 por página). 
2. Reporte de ocurrencias por servicio: agrupar registros por nombre de servicio y 
calcular: total de eventos, total de errores, porcentaje de fallos. Mostrar el Top 10. 
3. Corte de control por día: recorrer el árbol en orden secuencial y generar un listado 
con subtotales por cada día: cantidad de registros, desglose por origen. 
4. Detección de errores recurrentes: normalizar mensajes de error (eliminar timestamps 
variables, IDs numéricos, trace_ids), agrupar y mostrar el Top 5 de mensajes más 
frecuentes con sus fechas de primera y última ocurrencia. 
Módulo de excepciones personalizadas 
El sistema debe implementar al menos las siguientes excepciones: 
Excepción 
Cuándo se lanza 
InvalidTimestampError 
DuplicateEntryError 
El formato del timestamp no es válido. 
Se intenta insertar un registro duplicado exacto. 
UnknownLogFormatError El registro no coincide con ningún formato conocido. 
StorageCorruptionError El archivo de persistencia está corrupto. 
RangeNotFoundError 
Una búsqueda por rango no devuelve resultados. 
Estructuras auxiliares 
Además del Árbol B/B+, el sistema debe utilizar al menos una estructura auxiliar 
implementada desde cero: 
Estructura 
Uso sugerido 
Cola (Queue) Buffer de ingesta temporal antes de la inserción al árbol. 
Stack (Pila) 
Registro de operaciones para auditoría interna del sistema. 
Set 
Diccionario 
Detección rápida de duplicados (hash de timestamp + origen + mensaje). 
Índice secundario por nombre de servicio para consultas rápidas. 
Despliegue en AWS 
1. El código debe correr en una máquina virtual Linux (Ubuntu 20.04+ o Amazon Linux). 
10 
2. Crear un script de instalación (install.sh) que: actualice paquetes, instale Python 3.x, 
cree un entorno virtual, instale dependencias. 
3. Crear un script de ejecución (start_service.sh) que inicie la aplicación. 
4. Documentar en el README los pasos exactos para levantar una instancia EC2, 
incluyendo tipo de instancia sugerido (t2.micro o t3.micro). 
5. Realizar una prueba de carga que consista en la ingesta de al menos 50.000 
registros simulados y registrar los tiempos de inserción y búsqueda. 
Modelado UML obligatorio 
Los siguientes diagramas UML, los cuales deben ser consistentes con el código entregado. 
Cualquier discrepancia entre el modelo y la implementación se penalizará. 
Diagrama de clases 
Debe incluir: 
● Todas las clases del dominio. 
● Atributos con tipos y visibilidad (+ público, - privado, # protegido). 
● Métodos con firma completa (nombre, parámetros, tipo de retorno). 
● Relaciones: herencia, asociación, agregación (rombo blanco), composición (rombo 
negro). 
● Multiplicidad en todas las relaciones (1, 0..1, , 1..). 
● Estereotipos donde corresponda (<<interface>>, <<abstract>>). 
Diagrama de secuencia 
Debe incluir: 
● Flujos principales de al menos dos casos de uso a elección: 
● Mensajes síncronos y asíncronos donde corresponda. 
● Líneas de vida de los objetos participantes. 
● Bloques de iteración (loop) y alternativos (alt) donde corresponda. 
Memoria técnica y lo que se evaluará 
Documento que debe contener: 
1. Introducción: descripción del problema y justificación de la solución. 
2. Diagramas UML: clases y secuencia (al menos dos casos a elección) 
○ Diagrama de casos de uso: todos los actores identificados y relaciones 
include y extends donde corresponda. 
○ Inconsistencia UML-Código: si el diagrama de clases presenta atributos, 
métodos o relaciones que no están implementados en el código, o viceversa, 
se penalizará del puntaje de UML y documentación. 
11 
3. Fundamentación del Árbol B/B+: 
○ Explicación teórica del árbol elegido (definición, propiedades, orden). 
○ Justificación de por qué se eligió sobre una lista ordenada o un hash table. 
○ Análisis de complejidad: O(log n) para inserción y búsqueda. 
4. Justificación de diseño POO: 
○ Explicación de la jerarquía de clases elegida. 
○ Dónde se aplica polimorfismo y por qué. 
○ Cómo se garantiza el encapsulamiento. 
○ Dónde se aplican agregación y composición, justificando la diferencia. 
○ Consistencia en persistencia: el sistema debe demostrar que puede guardar 
el árbol en disco y restaurarlo completamente. Si al reiniciar la aplicación se 
pierden registros o la estructura del árbol queda corrupta, el trabajo no será 
considerado aprobado. 
○ Herencia: jerarquía de clases coherente y justificada. Uso apropiado de 
clases base abstractas y subclases específicas. 
○ Polimorfismo: Métodos como calcular_severidad() implementados de forma 
diferente en cada subclass. 
○ Encapsulamiento: uso correcto de protegido y privado para atributos 
sensibles. Acceso mediante métodos públicos/properties. 
○ Cohesión: cada clase debe tener responsabilidades claras y relacionadas. 
Los métodos deben operar sobre los propios datos de la clase. 
○ Acoplamiento: dependencias mínimas entre clases. Se debe preferir un bajo 
acoplamiento. 
○ Interfaces: uso de clases abstractas o interfaces (cuando aplique en Python) 
para definir contratos que otras clases implementen. 
○ Composición vs. herencia: justificación del uso de composición (rombo negro) 
frente a herencia cuando corresponda. Se debe evitar jerarquías 
innecesariamente profundas. 
○ Se evaluará la correcta aplicación de los principios de POO vistos en la 
cursada. 
5. Manual de despliegue en AWS: 
○ Pasos detallados para levantar la VM EC2. 
○ Configuración de seguridad (grupos de seguridad, puertos) si y solo si hace 
falta. 
○ Comandos de instalación y ejecución. 
6. Resultados de prueba de carga: 
○ Tabla con tiempos de inserción para 1.000, 10.000 y hasta 100.000 registros. 
○ Tiempos de búsqueda por rango para distintos tamaños. 
○ Capturas de pantalla del sistema en ejecución. 
Código Fuente 
El código debe cumplir con: 
● Modularidad: Separación clara de responsabilidades en paquetes. 
12 
● Naming conventions: Seguir PEP 8 (nombres de clases en PascalCase, funciones y 
variables en snake_case, constantes en UPPER_CASE). 
● Manejo de excepciones: Uso de try/except/finally con las excepciones personalizadas 
comentadas en el TP. 
● Nombres descriptivos: Prohibido el uso de variables como x, temp, func1, data2, etc. 
excepto en contadores de iteración simples (i, j). 
A tener en cuenta con la entrega: 
● Formato de citas: la memoria técnica debe seguir el formato APA para todas las citas 
y referencias bibliográficas. 
● Corrección de código: si el código entregado falla o no se ejecuta, el trabajo se 
considera no aprobado. Se otorga una única oportunidad de corrección dentro de las 
48 horas siguientes. 
● Defensa del TP no más de 15 minutos, pueden utilizar una PPT de guía. 
● Video demo (Opcional): se recomienda grabar un video de 5-10 minutos mostrando 
el funcionamiento del sistema. Puntos extra en la evaluación. 
● Fecha de entrega a convenir durante las fechas de presentación de finales. La 
entrega tiene que ser con antelación a la fecha del final y contar con al menos 2 
feedback. 
Pueden elegir implementar un Árbol B o un Árbol B+. Ambos son válidos. Las diferencias 
clave a considerar son: 
Árbol B: 
●  Las claves y los datos están distribuidos en todos los nodos (internos y hojas). 
●  La búsqueda por rango requiere recorrer el árbol en orden in-order. 
●  Es ligeramente más simple de implementar. 
Árbol B+: 
● Las claves están en los nodos internos, los datos solo en las hojas. 
● Las hojas están enlazadas entre sí. 
● La búsqueda por rango es más eficiente porque se recorre el enlace de hojas. 
● Es la estructura típica que usan las bases de datos reales para índices. 
Cualquiera de las dos opciones es válida para cumplir los objetivos del trabajo final. La 
elección debe justificarse en la memoria técnica según los pros y contras de cada una. 
13 
Material complementario 
Archivos de ingreso 
● logs_browser.txt 
● logs_api.txt 
● logs_alertas.txt 
● etc. 
Procesamiento 
● Parser (identifica tipo y extrae atributos) 
● Curador (normaliza y valida) 
● Objeto de Dominio X 
Core del sistema 
● Árbol B/B+ (nodos ordenados por timestamp) 
● Persistencia en archivo .db 
Salida 
● Búsqueda por rango temporal. 
● Reportes por servicio. 
● Cortes de control por día. 
● Errores recurrentes. 
14 
Bibliografía Recomendada 
1. Canning, J., Broder, A., & Lafore, R. (2022). Data Structures & Algorithms in Python. 
Addison-Wesley Professional. 
2. Fowler, M. (2004). UML distilled: A brief guide to the standard object modeling 
language. Addison-Wesley Professional. 
3. Jackson, C. (2009). Learning to program using Python. Cody Jackson. 
4. Martin, R. C. (2012). Código limpio: manual de estilo para el desarrollo ágil de 
software. 
5. Singh, N., Chouhan, S., & Verma, K. (2021). Object oriented programming: Concepts, 
limitations and application trends. TechRxiv. 
https://doi.org/10.36227/techrxiv.16677259.v1 
6. Kramer, J., & Hazzan, O. (2006). The role of abstraction in software engineering. 
ICSE'06. 
7. Liskov, B., & Guttag, J. (1986). Abstraction and specification in program development. 
MIT Press. 
8. Vera, J., & Vera, J. R. V. (2024). The role of object-oriented programming in 
sustainable and scalable software development. Minerva (Quito), 5(13), 59-68. 
https://doi.org/10.47460/minerva.v5i13.152 
9. Documentación oficial de Python. https://docs.python.org/3/ 
10. Visualización de estructuras de datos y algoritmos. VisuAlgo. https://visualgo.net/en














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
├── docs/                  # Memoria técnica y diagramas UML
│   ├── memoria_tecnica.md
│   ├── diagrama_clases.puml
│   ├── diagrama_casos_uso.puml
│   └── diagrama_secuencia.puml
└── README.md              # Este archivo
```

## Documentación de entrega

- [Memoria técnica](docs/memoria_tecnica.md)
- [Diagrama de clases](docs/diagrama_clases.puml)
- [Diagrama de casos de uso](docs/diagrama_casos_uso.puml)
- [Diagrama de secuencia](docs/diagrama_secuencia.puml)

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

El benchmark incluido mide por separado la inserción y una búsqueda por rango:

```bash
python load_test.py
```

La prueba ejecuta escenarios de 1.000, 10.000, 50.000 y 100.000 registros.
Los tiempos dependen del hardware y deben registrarse junto con el entorno de ejecución
en la memoria técnica.

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

