# OBJETIVO:
Implementar un sistema automatizado de clasificación de hortalizas que utiliza visión artificial y sensores físicos para categorizar brócoli según su estado de madurez (color) y dimensiones (tamaño). El sistema busca optimizar la producción agrícola local mediante una banda transportadora controlada por un ESP32 S3 CAM, la cual desvía automáticamente el producto de baja calidad, emite alertas sonoras y visuales, y permite el monitoreo remoto de estadísticas de producción a través de una interfaz web y notificaciones en la nube.

# INTEGRANTES:
- Mayra Paola Martínez Aranda(22240233) 
- Nissi Sarahi Prats Ramírez(23240003) 
- Erik Fabian Gonsalez Jimenez(23240022)  

# PROYECTO:
"BroccoSort AI: Sistema Automatizado de Clasificación de Hortalizas por Visión y Morfología"

# Descripcion
Proyecto de clasificación automatizada de brócoli con ESP32, MQTT y Python

### Instituto Tecnológico de León
**Materia:** Sistemas Programables (ISC)  
**Profesor:** MA VERONICA TAPIA IBARRA
**Fecha de Entrega:** 20 de mayo de 2026  

---

## Objetivo General del Dashboard e Interfaz de Usuario
Garantizar la supervisión perimetral y la persistencia de datos en la nube mediante un ecosistema IoT integrado con **Firebase Realtime Database**. La interfaz gráfica desarrollada faculta el monitoreo síncrono de las variables morfológicas del entorno (distancia del sensor ultrasónico, niveles de iluminación local LDR y el estado de tránsito por sensor infrarrojo). 

Asimismo, provee un canal de **Control Bidireccional Activo** que permite al operador de la planta enviar comandos remotos inmediatos (Arrancar/Parar) sobre el Puente H de la banda transportadora para detener el flujo ante contingencias operativas.

## Políticas de Privacidad y Cumplimiento de Datos Visuales
En estricto apego a las buenas prácticas de la ingeniería de software y la seguridad informática, el sistema cuenta con un esquema de protección de datos:
* **Inferencia Local Efímera:** Las capturas binarias JPEG solicitadas a la `ESP32-CAM` se procesan únicamente en la memoria RAM del servidor Python para la obtención de la clase por el SDK de Roboflow.
* **Anonimización en la Nube:** Queda totalmente restringido y deshabilitado el almacenamiento de imágenes, rostros o entornos físicos en la base de datos de Firebase. 
* **Persistencia de Metadatos:** Los únicos datos transmitidos a la nube son métricas de rendimiento puramente vectoriales (Nombre de la clase identificada, marcas de tiempo y el porcentaje matemático de confianza de la predicción).
