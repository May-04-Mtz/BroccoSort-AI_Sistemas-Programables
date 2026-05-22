# NOMBRE DEL PROYECTO: BroccoSort AI
# INTEGRANTES: Mayra Paola Martinez Aranda, Nissi Sarahi Prats Ramirez, Erik Fabian Gonsalez Jimenez
# DESCRIPCIÓN: Programa principal coordinado con arquitectura MQTT de 4 niveles obligatorios.

import time
from umqtt.simple import MQTTClient
from dispositivos import SensorBox, ActuatorBox

# =====================================================================
# 🔴 ARQUITECTURA DE TÓPICOS ESTÁNDAR 4 NIVELES (REGLA DE LA MAESTRA) 🔴
# =====================================================================
MQTT_BROKER = "broker.hivemq.com" 
CLIENT_ID = "ESP32_BroccoSort_Banda"

TOPICO_PRESENCIA = "broccosort/banda01/presencia/sensor01"
TOPICO_DISTANCIA = "broccosort/banda01/distancia/sensor02"
TOPICO_BANDA     = b"broccosort/banda01/banda/actuador01"
TOPICO_BRAZO     = b"broccosort/banda01/brazo/actuador02"

# --- INICIALIZACIÓN ---
sensores = SensorBox()
actuadores = ActuatorBox()
banda_activa = False

def mensaje_recibido(topic, msg):
    global banda_activa
    dato = msg.decode()
    print(f"📩 Comando Recibido [{topic.decode()}]: {dato}")
    
    if topic == TOPICO_BANDA:
        if dato == "1":
            banda_activa = True
            actuadores.control_banda(True)
            print("▶️ Banda en marcha")
        else:
            banda_activa = False
            actuadores.estado_seguro()
            print("🛑 Parada desde la aplicación")
            
    elif topic == TOPICO_BRAZO:
        angulo = int(dato)
        actuadores.mover_brazo_clasificador(angulo)
        if angulo == 180:   
            actuadores.activar_alerta_error(0.6)
        elif angulo == 90:  
            actuadores.activar_alerta_error(0.15)

def conectar():
    cliente = MQTTClient(CLIENT_ID, MQTT_BROKER)
    cliente.set_callback(mensaje_recibido)
    cliente.connect()
    cliente.subscribe(TOPICO_BANDA)
    cliente.subscribe(TOPICO_BRAZO)
    print("✅ Conexión MQTT exitosa bajo estructura de 4 niveles")
    return cliente

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
            mqtt.check_msg()
            datos = sensores.obtener_resumen_sensores()
            
            if time.time() - ultimo_envio > 0.5:
                # Envío de telemetría estructurada para árbol NoSQL sin corrupciones
                mqtt.publish(TOPICO_PRESENCIA, "1" if datos["presencia"] else "0")
                mqtt.publish(TOPICO_DISTANCIA, "{:.1f}".format(datos["distancia"]))
                ultimo_envio = time.time()

        except Exception as e:
            print(f"⚠️ Error en bucle: {e}")
            time.sleep(2)
            mqtt = conectar()

if __name__ == "__main__":
    ejecutar()
