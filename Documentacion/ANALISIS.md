# OBJETIVO:
Implementar un sistema automatizado de clasificación de hortalizas que utiliza visión artificial y sensores físicos para categorizar brócoli según su estado de madurez (color) y dimensiones (tamaño). El sistema busca optimizar la producción agrícola local mediante una banda transportadora controlada por un ESP32 S3 CAM, la cual desvía automáticamente el producto de baja calidad, emite alertas sonoras y visuales, y permite el monitoreo remoto de estadísticas de producción a través de una interfaz web y notificaciones en la nube.

# INTEGRANTES:

Mayra Paola Martínez Aranda(22240233) 

Nissi Sarahi Prats Ramírez(23240003) 

Erik Fabian Gonsalez Jimenez(23240022) 

# PROYECTO:
"BroccoSort AI: Sistema Automatizado de Clasificación de Hortalizas por Visión y Morfología"

# Análisis Individual de Integrantes - BroccoSort AI

Este documento detalla los retos técnicos y las soluciones aplicadas por cada miembro del equipo durante la integración MQTT.

---

## 1. Mayra Paola Martínez Aranda
* **Problema**: Inestabilidad al publicar datos tipo `float` (decimales) del sensor ultrasónico directamente por el protocolo MQTT.
* **Solución**: Se implementó una capa de conversión a `string` en la ESP32 antes del envío y una lógica de reconversión a `float` en el servidor Python para procesar las dimensiones con precisión.
* **Conclusión**: El uso de la HAL (Capa de Abstracción de Hardware) permitió separar la lógica de lectura física de la lógica de comunicación, facilitando las pruebas de software.

## 2. Nissi Sarahi Prats Ramírez
* **Problema**: Pérdida intermitente de conexión con el Broker MQTT debido a la interferencia electromagnética generada por el motor de la banda transportadora.
* **Solución**: Se integró un bloque `try-except` en el loop principal de MicroPython para gestionar excepciones de red y forzar la reconexión automática del cliente MQTT sin detener el programa.
* **Conclusión**: La robustez de un sistema IoT depende críticamente de una gestión de errores eficiente en la capa de comunicación.

## 3. Erik Fabián González Jiménez
* **Problema**: Latencia excesiva entre la detección del brócoli por los sensores y el accionamiento del servomotor clasificador.
* **Solución**: Se optimizaron los tiempos de espera (`time.sleep`) en el script principal y se ajustaron los *callbacks* de suscripción MQTT para que la respuesta a los comandos sea inmediata.
* **Conclusión**: El protocolo MQTT demostró ser ideal para el proyecto BroccoSort AI por su ligereza y su capacidad de respuesta casi en tiempo real.
