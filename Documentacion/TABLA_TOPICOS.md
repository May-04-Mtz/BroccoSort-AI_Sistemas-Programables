# OBJETIVO:
Implementar un sistema automatizado de clasificación de hortalizas que utiliza visión artificial y sensores físicos para categorizar brócoli según su estado de madurez (color) y dimensiones (tamaño). El sistema busca optimizar la producción agrícola local mediante una banda transportadora controlada por un ESP32 S3 CAM, la cual desvía automáticamente el producto de baja calidad, emite alertas sonoras y visuales, y permite el monitoreo remoto de estadísticas de producción a través de una interfaz web y notificaciones en la nube.

# INTEGRANTES:

Mayra Paola Martínez Aranda(22240233) (Código)

Nissi Sarahi Prats Ramírez(23240003) (Código)

Erik Fabian Gonsalez Jimenez(23240022) (Código)

# PROYECTO:
"BroccoSort AI: Sistema Automatizado de Clasificación de Hortalizas por Visión y Morfología"

# Matriz de Tópicos MQTT - BroccoSort AI
Este documento detalla la jerarquía de comunicación entre la ESP32 y el servidor Python.

| Dispositivo | Tópico | Dirección | Descripción |
| :--- | :--- | :--- | :--- |
| **Ultrasonico** | `broccosort/telemetria/distancia` | ESP32 -> PC | Envía altura del brócoli en cm |
| **Infrarrojo** | `broccosort/telemetria/presencia` | ESP32 -> PC | Detecta si hay producto (0/1) |
| **LDR** | `broccosort/telemetria/luz` | ESP32 -> PC | Nivel de iluminación para la cámara |
| **Servomotor** | `broccosort/comando/brazo` | PC -> ESP32 | Ángulo de clasificación (0, 90, 180) |
| **Motor Banda** | `broccosort/comando/banda` | PC -> ESP32 | Control de movimiento (0/1) |
| **Buzzer** | `broccosort/comando/alerta` | PC -> ESP32 | Activa sonido en caso de error |
