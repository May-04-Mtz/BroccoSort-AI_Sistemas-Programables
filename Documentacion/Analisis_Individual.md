# OBJETIVO:
Implementar un sistema automatizado de clasificación de hortalizas que utiliza visión artificial y sensores físicos para categorizar brócoli según su estado de madurez (color) y dimensiones (tamaño). El sistema busca optimizar la producción agrícola local mediante una banda transportadora controlada por un ESP32 S3 CAM, la cual desvía automáticamente el producto de baja calidad, emite alertas sonoras y visuales, y permite el monitoreo remoto de estadísticas de producción a través de una interfaz web y notificaciones en la nube.

# INTEGRANTES:
- Mayra Paola Martínez Aranda(22240233) 
- Nissi Sarahi Prats Ramírez(23240003) 
- Erik Fabian Gonsalez Jimenez(23240022)  

# PROYECTO:
"BroccoSort AI: Sistema Automatizado de Clasificación de Hortalizas por Visión y Morfología"

# Análisis Individual de Integrantes - BroccoSort AI

Este documento detalla los retos técnicos y las soluciones aplicadas por cada miembro del equipo durante la integración MQTT.

---

### 1. Mayra Paola Martínez Aranda
* **Clave de Estudiante:** 22240233
* **Rol en el Pipeline:** Infraestructura de Red, Conectividad y HAL (Hardware Abstraction Layer)
#### Problema en Red e Infraestructura
Inestabilidad al publicar datos tipo `float` (decimales) del sensor ultrasónico directamente por el protocolo MQTT. Asimismo, durante la integración del pipeline de Inteligencia Artificial, la solicitud HTTP (`requests.get`) realizada desde el servidor central de Python hacia la **ESP32-CAM** fallaba de forma intermitente debido a que la placa cambiaba dinámicamente de dirección IP por asignación DHCP al reiniciarse o perder energía en la maqueta, perdiendo la sincronización con el modelo de clasificación.

#### Solución Aplicada
Se implementó una capa de conversión de tipos a `string` en el MicroPython de la ESP32 antes del envío por red, añadiendo una lógica inversa de reconversión en el servidor Python central. Adicionalmente, se modificó la configuración de red en la función `conectar_wifi()` dentro del archivo de la cámara forzando una **dirección IP estática fija** (`192.168.8.27`) mediante la sub-librería `wlan.ifconfig()`, garantizando la disponibilidad inmediata y predecible del recurso web de captura de imágenes.

#### Conclusión
El uso de una HAL (Capa de Abstracción de Hardware) permite aislar por completo la lógica de lectura física de las variables de comunicación de red. Del mismo modo, la predictibilidad de la infraestructura local mediante direccionamiento estático en entornos perimetrales es obligatoria para evitar la caída total de un pipeline continuo de datos distribuidos en tiempo real.

---

### 2. Nissi Sarahi Prats Ramírez
* **Clave de Estudiante:** 23240003
* **Rol en el Pipeline:** Gestión de Errores y Preprocesamiento de Respuestas de la IA

#### Problema en Gestión de Errores e IA
Pérdida intermitente de la conexión con el Broker MQTT debido a la interferencia electromagnética severa generada por las bobinas del motor DC de la banda transportadora. Adicionalmente, el modelo de clasificación de IA (Roboflow Inference API) generaba fallos de sintaxis en el intérprete del servidor central al retornar etiquetas con caracteres especiales o acentos (por ejemplo, `'floración'` vs `'floracion'`), lo que provocaba que la lógica condicional no reconociera la clase e introdujera comportamientos erráticos o nulos en los actuadores.

#### Solución Aplicada
Se integró estructuralmente un bloque de manejo de excepciones `try-except` dentro del loop principal de ejecución en MicroPython para interceptar fallos del socket de red y forzar la reconexión automática del cliente sin detener la banda transportadora. Para mitigar los fallos de la IA, se implementó una rutina de normalización del payload JSON en Python usando métodos de limpieza de cadenas como `.lower().strip()` complementado con operadores lógicos de pertenencia (`any`), aislando la toma de decisiones críticas de cualquier variación ortográfica del modelo.

#### Conclusión
La robustez física de un ecosistema IoT industrializado depende estrictamente de una tolerancia a fallos eficiente implementada a nivel software en la capa de comunicación. Además, el codiseño de sistemas ciberfísicos inteligentes requiere de filtros avanzados de normalización de datos antes de traducir una inferencia probabilística en un comando motriz directo sobre el actuador.

---

### 3. Erik Fabián González Jiménez
* **Clave de Estudiante:** 23240022
* **Rol en el Pipeline:** Sincronización Temporal, Optimización de Latencia y Actuación Física

#### Problema en Latencia y Sincronización
Se presentó una latencia excesiva en el bucle cerrado del sistema: desde que los sensores detectaban la hortaliza hasta el accionamiento físico del servomotor clasificador. Este problema se agravó exponencialmente al acoplar el procesamiento de imágenes, ya que el tiempo de ida y vuelta de la red combinado con la inferencia de la red neuronal en el servidor central retrasaba la respuesta mecánica, causando que el brazo clasificador golpeara el brócoli fuera de tiempo o cuando ya había avanzado demasiado en la banda transportadora.

#### Solución Aplicada
Se optimizaron minuciosamente los delays de control (`time.sleep`) en el script de MicroPython y se reestructuraron los callbacks de suscripción MQTT para acelerar el procesamiento de interrupciones de red. Paralelamente, se ajustaron los tiempos de retención mecánica en el servidor de Python a un delta estricto de `time.sleep(2.5)`, forzando una publicación inmediata de retorno al estado seguro (`0°`) tras enviar la instrucción de clasificación, sincronizando la velocidad algorítmica con el avance mecánico real de la maqueta.

#### Conclusión
El protocolo MQTT demuestra ser una tecnología idónea en IoT debido a su ligereza basada en publicación/suscripción. Sin embargo, la viabilidad operativa de la inteligencia perimetral integrada depende del balanceo preciso de las cargas de trabajo; la latencia acumulada por la inferencia de IA y el tráfico de red debe estar calibrada matemáticamente en relación directa con las constantes mecánicas y físicas del hardware empleado.
