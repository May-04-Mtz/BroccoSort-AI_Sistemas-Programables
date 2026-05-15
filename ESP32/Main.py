"""
# OBJETIVO:
Implementar un sistema automatizado de clasificación de hortalizas que utiliza visión artificial y sensores 
físicos para categorizar brócoli según su estado de madurez (color) y dimensiones (tamaño). El sistema busca 
optimizar la producción agrícola local mediante una banda transportadora controlada por un ESP32 S3 CAM, l
a cual desvía automáticamente el producto de baja calidad, emite alertas sonoras y visuales, y permite el monitoreo
remoto de estadísticas de producción a través de una interfaz web y notificaciones en la nube.

# INTEGRANTES:
- Mayra Paola Martínez Aranda(22240233) 
- Nissi Sarahi Prats Ramírez(23240003) 
- Erik Fabian Gonsalez Jimenez(23240022)  

# PROYECTO:
"BroccoSort AI: Sistema Automatizado de Clasificación de Hortalizas por Visión y Morfología"
"""

# NOMBRE DEL PROYECTO: BroccoSort AI
# INTEGRANTES: Mayra Paola Martinez Aranda, Nissi Sarahi Prats Ramirez, Erik Fabian Gonsalez Jimenez
# DESCRIPCIÓN: Programa principal coordinado con MQTT para clasificación y control remoto.

import time
from umqtt.simple import MQTTClient
from dispositivos import SensorBox, ActuatorBox

# --- CONFIGURACIÓN MQTT ---
MQTT_BROKER = "broker.hivemq.com" # Broker público para que funcione con la App
CLIENT_ID = "ESP32_BroccoSort_Sistemas"
TOPICO_PRESENCIA = "broccosort/telemetria/presencia"
TOPICO_DISTANCIA = "broccosort/telemetria/distancia"
TOPICO_BANDA     = b"broccosort/comando/banda"
TOPICO_BRAZO     = b"broccosort/comando/brazo"

# --- INICIALIZACIÓN ---
sensores = SensorBox()
actuadores = ActuatorBox()
banda_activa = False

# --- FUNCIÓN DE RECEPCIÓN (CALLBACK) ---
def mensaje_recibido(topic, msg):
    global banda_activa
    dato = msg.decode()
    print(f"📩 Comando recibido [{topic.decode()}]: {dato}")
    
    # Control de la banda desde la App
    if topic == TOPICO_BANDA:
        if dato == "1":
            banda_activa = True
            actuadores.control_banda(True)
            print("▶️ Banda en marcha")
        else:
            banda_activa = False
            actuadores.estado_seguro()
            print("🛑 Parada de emergencia/App")
            
    # Control del brazo desde la IA (Python)
    elif topic == TOPICO_BRAZO:
        angulo = int(dato)
        actuadores.mover_brazo_clasificador(angulo)
        if angulo == 180: # Si la IA detectó podrido
            actuadores.activar_alerta_error(0.5)

# --- CONEXIÓN AL BROKER ---
def conectar():
    cliente = MQTTClient(CLIENT_ID, MQTT_BROKER)
    cliente.set_callback(mensaje_recibido)
    cliente.connect()
    cliente.subscribe(TOPICO_BANDA)
    cliente.subscribe(TOPICO_BRAZO)
    print("✅ Conexión MQTT exitosa")
    return cliente

# --- BUCLE PRINCIPAL ---
def ejecutar():
    try:
        mqtt = conectar()
    except:
        print("❌ Fallo de red. Reiniciando...")
        time.sleep(5)
        return

    print("BroccoSort AI operativo...")
    ultimo_envio = 0

    while True:
        try:
            # 1. Revisar si hay órdenes de la App o IA
            mqtt.check_msg()
            
            # 2. Leer sensores
            datos = sensores.obtener_resumen_sensores()
            
            # 3. Reportar a la App y al Servidor cada 0.5 seg
            if time.time() - ultimo_envio > 0.5:
                # Enviar presencia (0 o 1)
                mqtt.publish(TOPICO_PRESENCIA, "1" if datos["presencia"] else "0")
                # Enviar distancia para la gráfica de la App
                mqtt.publish(TOPICO_DISTANCIA, "{:.1f}".format(datos["distancia"]))
                ultimo_envio = time.time()

            # 4. Lógica de respaldo (Si no hay internet, el sistema sigue clasificando)
            if datos["presencia"] and not banda_activa:
                # Solo log local si la banda está apagada
                pass 

        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(2)
            mqtt = conectar()

if __name__ == "__main__":
    ejecutar()
