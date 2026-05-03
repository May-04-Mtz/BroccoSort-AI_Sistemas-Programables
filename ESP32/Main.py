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

from dispositivos import SensorBox, ActuatorBox
import time

# Inicialización
sensores = SensorBox()
actuadores = ActuatorBox()

print("BroccoSort AI iniciado...")

while True:
    try:
        # 1. Monitorear sensores
        datos = sensores.obtener_resumen_sensores()
        
        # 2. Lógica: Si hay un brócoli presente
        if datos["presencia"]:
            print("Brócoli detectado. Distancia: {:.1f}cm".format(datos["distancia"]))
            
            # Clasificación por tamaño (ejemplo: menos de 10cm es cabeza grande)
            if datos["distancia"] < 10:
                actuadores.mover_brazo_clasificador(90) # Recipiente Tamaño
            else:
                actuadores.mover_brazo_clasificador(0)  # Recipiente Maduro
        
        time.sleep(0.5)
        
    except KeyboardInterrupt:
        # Forzar estado seguro al detener con Ctrl+C
        actuadores.estado_seguro()
        break
