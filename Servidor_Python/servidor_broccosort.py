"""
# ------------------------------------------------------------------
# PROYECTO: BroccoSort AI: Sistema Automatizado de Clasificación
#           de Hortalizas por Visión y Morfología
# INTEGRANTES:
# - Mayra Paola Martínez Aranda (22240233)
# - Nissi Sarahi Prats Ramírez (23240003)
# - Erik Fabian Gonsalez Jimenez (23240022)
# DESCRIPCIÓN: Servidor Backend que suscribe a los tópicos MQTT
#              y persiste el historial estructurado en Firebase (NoSQL).
# ------------------------------------------------------------------
"""
import time
import json
import requests
import paho.mqtt.client as mqtt

# ==========================================
# ☁️ CONFIGURACIÓN NUBE Y RED ☁️
# ==========================================
FIREBASE_URL = "https://broccosort-ai-default-rtdb.firebaseio.com"
BROKER_MQTT = "broker.hivemq.com" # Debe coincidir con DATASET_2
PUERTO_MQTT = 1883

# Suscripción comodín a toda la jerarquía de la banda 01
TOPICO_ESCUCHA = "broccosort/+/banda01/+"

def on_connect(client, userdata, flags, rc):
    print(f"✅ Backend Conectado al Broker MQTT. Código: {rc}")
    client.subscribe(TOPICO_ESCUCHA)
    print(f"📡 Escuchando telemetría en la jerarquía: {TOPICO_ESCUCHA}")

def on_message(client, userdata, msg):
    topico = msg.topic
    payload = msg.payload.decode('utf-8')
    print(f"📩 [MQTT] Recibido -> Tópico: {topico} | Dato: {payload}")

    # Filtrar solo cuando el brazo se mueve (significa que hubo clasificación de IA)
    if "brazo" in topico:
        angulo = int(payload)
        
        # Reconstrucción de estado basado en la lógica de control
        clase_detectada = "fresco" if angulo == 0 else "maduro" if angulo == 90 else "podrido"
        
        # 1. Obtener longitud actual de la base de datos para crear el índice (14, 15, 16...)
        url_historial = f"{FIREBASE_URL}/historial_json.json"
        try:
            res_get = requests.get(url_historial)
            datos_actuales = res_get.json()
            siguiente_id = len(datos_actuales) if isinstance(datos_actuales, list) else 0

            # 2. Armar el árbol JSON exacto que requiere el Dashboard
            payload_firebase = {
                "clase": clase_detectada,
                "confianza": 0.96, # Valor referencial alto
                "timestamp": int(time.time())
            }

            # 3. Subir el nodo a Firebase Realtime Database
            url_dest = f"{FIREBASE_URL}/historial_json/{siguiente_id}.json"
            res_put = requests.put(url_dest, json=payload_firebase)

            if res_put.status_code == 200:
                print(f"☁️ [Firebase] Registro [{siguiente_id}] persistido con éxito: {clase_detectada.upper()}")
            else:
                print(f"❌ [Firebase] Error al guardar. Código HTTP: {res_put.status_code}")

        except Exception as e:
            print(f"⚠️ Error de sincronización NoSQL: {e}")

# Inicialización y ciclo de vida del servidor
cliente_bd = mqtt.Client()
cliente_bd.on_connect = on_connect
cliente_bd.on_message = on_message

print("⚙️  Iniciando Backend Logger BroccoSort...")
cliente_bd.connect(BROKER_MQTT, PUERTO_MQTT, 60)

# Mantiene el script en ejecución permanente escuchando la red
cliente_bd.loop_forever()
