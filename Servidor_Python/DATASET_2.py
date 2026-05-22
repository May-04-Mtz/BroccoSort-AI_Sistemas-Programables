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

import os
import time
import requests  
import paho.mqtt.client as mqtt
from roboflow import Roboflow
from datetime import datetime

# =====================================================================
# 🔴 CONFIGURACIONES ESTRUCTURADAS (4 NIVELES) 🔴
# =====================================================================
BROKER_MQTT = "broker.hivemq.com"  
PUERTO_MQTT = 1883 

# Ajuste estricto de tópicos para alineación con base de datos NoSQL
TOPICO_PRESENCIA = "broccosort/presencia/banda01/sensor01"
TOPICO_BRAZO = "broccosort/brazo/banda01/actuador02"

ESP32_CAM_URL = "http://192.168.8.27/foto" 
IMAGEN_TEMPORAL = "captura_banda.jpg"
FIREBASE_URL = "https://broccosort-ai-default-rtdb.firebaseio.com/historial.json"

client = mqtt.Client()
objeto_en_espera = False  

# --- Configuración de Roboflow ---
print("⏳ Inicializando modelo de IA...")
rf = Roboflow(api_key="T5jPuaVg9YZzFQq277bt")
project = rf.workspace().project("broccoli-6n3ht-ininr")
model = project.version(3).model
print("✅ IA de Roboflow cargada exitosamente.")

def guardar_en_firebase(estado, confianza):
    """Envía el registro de clasificación a Firebase Realtime Database"""
    try:
        historial_clasificacion = {
            "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "estado": estado,
            "confianza": round(confianza * 100, 2)
        }
        respuesta = requests.post(FIREBASE_URL, json=historial_clasificacion, timeout=3)
        if respuesta.status_code == 200:
            print("☁️ Datos respaldados en Firebase correctamente sin comprometer el árbol JSON.")
        else:
            print(f"⚠️ Firebase rechazó los datos. Código: {respuesta.status_code}")
    except Exception as e:
        print(f"❌ Error al conectar con Firebase: {e}")

def procesar_clasificacion(client):
    try:
        print("\n📸 Detectado. Solicitando captura a la ESP32-CAM...")
        respuesta = requests.get(ESP32_CAM_URL, timeout=5)
        
        if respuesta.status_code == 200:
            with open(IMAGEN_TEMPORAL, 'wb') as f:
                f.write(respuesta.content)
            
            prediction = model.predict(IMAGEN_TEMPORAL, confidence=25).json()
            detecciones = prediction["predictions"]

            if len(detecciones) > 0:
                clases_encontradas = [det["class"].lower().strip() for det in detecciones]
                clase_principal = detecciones[0]["class"]
                confianza_principal = detecciones[0]["confidence"]
                
                for det in detecciones:
                    print(f"🎯 DETECTADO: {det['class']} ({det['confidence'] * 100:.1f}%)")

                # Lógica de toma de decisiones mapeada a actuadores
                if any("podrido" in c for c in clases_encontradas):
                    print("🚨 RECHAZADO: Estado podrido. Moviendo brazo a 180°.")
                    client.publish(TOPICO_BRAZO, "180")
                    guardar_en_firebase("podrido", confianza_principal)
                    time.sleep(2.5)  
                    client.publish(TOPICO_BRAZO, "0")

                elif any("floracion" in c for c in clases_encontradas) or any("floración" in c for c in clases_encontradas):
                    print("⚠️ FLORACIÓN: Calidad media. Moviendo brazo a 90°.")
                    client.publish(TOPICO_BRAZO, "90")
                    guardar_en_firebase("floracion", confianza_principal)
                    time.sleep(2.5)
                    client.publish(TOPICO_BRAZO, "0")
                else:
                    print("🍏 APTO: Brócoli óptimo. Sigue curso a 0°.")
                    client.publish(TOPICO_BRAZO, "0")
                    guardar_en_firebase("apto", confianza_principal)
            else:
                print("❓ Clasificación ambigua. Pasa por defecto.")
                client.publish(TOPICO_BRAZO, "0")
                guardar_en_firebase("indeterminado", 0.0)
        else:
            print("❌ Error: La cámara no respondió.")
    except Exception as e:
        print(f"⚠️ Fallo en el bucle de la IA: {e}")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("🌐 Servidor de IA conectado al Broker bajo estándar de 4 niveles")
        client.subscribe(TOPICO_PRESENCIA)
    else:
        print(f"❌ Fallo de conexión. Código: {rc}")

def on_message(client, userdata, msg):
    global objeto_en_espera
    valor = msg.payload.decode()
    
    if valor == "1" and not objeto_en_espera:
        objeto_en_espera = True
        procesar_clasificacion(client)
    elif valor == "0":
        objeto_en_espera = False  

if __name__ == "__main__":
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_MQTT, PUERTO_MQTT, 60)
    client.loop_forever()
