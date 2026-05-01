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
