"""
OBJETIVO: Establecer el ecosistema de comunicación MQTT entre ESP32 y Python para el pesaje y clasificación.
INTEGRANTES: 
- Mayra Paola Martinez Aranda (Código)
- Nissi Sarahi Prats Ramirez (Código)
- Erik Fabian Gonsalez Jimenez (Código)
PROYECTO: BroccoSort AI
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
