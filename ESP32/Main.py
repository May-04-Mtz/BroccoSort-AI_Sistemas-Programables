"""
OBJETIVO:
Coordinar el sistema de clasificación mediante la integración de la HAL y el protocolo MQTT. 
Publica telemetría constante y reacciona a comandos remotos para la clasificación de hortalizas.

INTEGRANTES:
- Mayra Paola Martínez Aranda (22240233) 
- Nissi Sarahi Prats Ramírez (23240003) 
- Erik Fabian Gonsalez Jimenez (23240022)  

PROYECTO:
"BroccoSort AI: Sistema Automatizado de Clasificación de Hortalizas por Visión y Morfología"
"""

from dispositivos import SensorBox, ActuatorBox
from comunicacion_mqtt import MQTTHandler
import time

# 1. Inicialización de Hardware (HAL)
sensores = SensorBox()
actuadores = ActuatorBox()

# 2. Inicialización de Comunicación (Broker)
# Reemplaza con la IP de tu servidor o broker público
mqtt = MQTTHandler(broker="broker.hivemq.com", client_id="ESP32_BroccoSort_01", actuadores=actuadores)

print("Iniciando BroccoSort AI con soporte MQTT...")

try:
    mqtt.conectar()
except Exception as e:
    print("Error conectando al broker:", e)

while True:
    try:
        # Requisito: Revisar si han llegado comandos del servidor Python
        mqtt.client.check_msg() 

        # 3. Lectura de Sensores vía HAL
        datos = sensores.obtener_resumen_sensores()
        
        # 4. Publicación de Telemetría (Mapeo 100% de sensores)
        # Esto envía distancia, presencia y luz automáticamente al servidor
        mqtt.publicar_telemetria(datos)
        
        # 5. Lógica de control local / Monitoreo
        if datos["presencia"]:
            print("Brócoli en banda. Enviando datos a telemetría...")
            
            # Lógica automática de respaldo si no hay comandos externos
            if datos["distancia"] < 10:
                actuadores.mover_brazo_clasificador(90)
            else:
                actuadores.mover_brazo_clasificador(0)
        
        time.sleep(0.5) # Delay para no saturar el broker
        
    except KeyboardInterrupt:
        print("Deteniendo sistema...")
        actuadores.estado_seguro()
        break
    except Exception as e:
        print("Error en el bucle principal:", e)
        # Intento de reconexión automática si se cae el Wi-Fi/MQTT
        time.sleep(5)
        continue
