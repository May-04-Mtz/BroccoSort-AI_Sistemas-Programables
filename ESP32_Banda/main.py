"""
NOMBRE DEL PROYECTO: BroccoSort AI: Sistema Automatizado de Clasificación
de Hortalizas por Visión y Morfología
OBJETIVO: Integración de IA para Captura remota y transmisión de imágenes
de hortalizas hacia el servidor central de IA.
INTEGRANTES: 
- Mayra Paola Martínez Aranda (22240233)
- Nissi Sarahi Prats Ramírez (23240003)
- Erik Fabian Gonsalez Jimenez (23240022)
"""

import time
from dispositivos import SensorBox, ActuatorBox
from comunicacion_mqtt import MQTTHandler

# Configuraciones base de la infraestructura
MQTT_BROKER = "broker.hivemq.com" 
CLIENT_ID = "ESP32_BroccoSort_Banda"

# Inicialización de componentes físicos (HAL)
sensores = SensorBox()
actuadores = ActuatorBox()

# Vinculación del manejador de comunicación pasándole la instancia de hardware
comunicacion = MQTTHandler(MQTT_BROKER, CLIENT_ID, actuadores)

def ejecutar():
    try:
        comunicacion.conectar()
    except Exception as e:
        print(f"❌ Fallo de red al conectar Broker: {e}. Reintentando en 5s...")
        time.sleep(5)
        return

    print("🚀 Sistema BroccoSort AI en marcha y sincronizado...")
    ultimo_envio = 0

    while True:
        try:
            # Revisa de forma asíncrona si hay comandos desde la laptop o dashboard
            comunicacion.client.check_msg()
            
            # Captura de datos en tiempo real desde los sensores estables
            datos_sensores = sensores.obtener_resumen_sensores()
            
            # Envío de telemetría temporizado cada 500ms para evitar saturación de red
            if time.time() - ultimo_envio > 0.5:
                comunicacion.publicar_telemetria(datos_sensores)
                ultimo_envio = time.time()

        except Exception as e:
            print(f"⚠️ Alerta en bucle de ejecución: {e}. Intentando restablecer enlaces...")
            time.sleep(2)
            try:
                comunicacion.conectar()
            except:
                pass

if __name__ == "__main__":
    ejecutar()
