"""
OBJETIVO:
Implementar un sistema automatizado de clasificación de hortalizas que utiliza visión artificial y sensores físicos para categorizar brócoli según su estado de madurez (color) y dimensiones (tamaño). El sistema busca optimizar la producción agrícola local mediante una banda transportadora controlada por un ESP32 S3 CAM, la cual desvía automáticamente el producto de baja calidad, emite alertas sonoras y visuales, y permite el monitoreo remoto de estadísticas de producción a través de una interfaz web y notificaciones en la nube.

INTEGRANTES:

Mayra Paola Martínez Aranda (Código)

Nissi Sarahi Prats Ramírez (Código)

Erik Fabian Gonsalez Jimenez (Código)

PROYECTO:
"BroccoSort AI: Sistema Automatizado de Clasificación de Hortalizas por Visión y Morfología"
"""

# Configuración de Red (Sustituir con datos reales para pruebas locales)
WIFI_SSID = "TU_RED_WIFI"
WIFI_PASSWORD = "TU_CONTRASEÑA"

# Configuración MQTT
MQTT_BROKER = "192.168.x.x" # IP de la PC con el servidor Python
TOPICO_DISTANCIA = "broccosort/telemetria/distancia"
