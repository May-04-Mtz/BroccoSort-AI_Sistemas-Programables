"""
# ------------------------------------------------------------------
# PROYECTO: BroccoSort AI: Sistema Automatizado de Clasificación
#           de Hortalizas por Visión y Morfología
# INTEGRANTES:
# - Mayra Paola Martínez Aranda (22240233)
# - Nissi Sarahi Prats Ramírez (23240003)
# - Erik Fabian Gonsalez Jimenez (23240022)
# OBJETIVO: Integración de IA para captura remota de imágenes, 
#              inferencia con Roboflow y publicación de comandos MQTT.
# ------------------------------------------------------------------
"""
import os
import time
import requests
import paho.mqtt.client as mqtt
from roboflow import Roboflow
from datetime import datetime

# ==========================================
# 🔴 CONFIGURACIONES ESTRUCTURADAS (4 NIVELES) 🔴
# ==========================================
BROKER_MQTT = "broker.hivemq.com"  # Cambiar por la IP de tu broker si es local
PUERTO_MQTT = 1883
TOPICO_BRAZO = "broccosort/brazo/banda01/actuador02"
TOPICO_BANDA = "broccosort/banda/banda01/actuador01"

# ==========================================
# 🟢 CREDENCIALES ROBOFLOW E IMAGEN 🟢
# ==========================================
RF_API_KEY = "Yhhcj1bdoRo0Cavl2jZV"
MODEL_ID = "broccoli-8syka-yrzti"
VERSION = 2

# Ajusta esta IP a la de la ESP32-CAM o IP Webcam del celular
URL_CAMARA = "http://192.168.200.50:8080/photo.jpg" 

def on_connect(client, userdata, flags, rc):
    print(f"✅ [MQTT] Enlace establecido con el Broker. Código de estado: {rc}")

# Inicialización MQTT
cliente_mqtt = mqtt.Client()
cliente_mqtt.on_connect = on_connect
cliente_mqtt.connect(BROKER_MQTT, PUERTO_MQTT, 60)
cliente_mqtt.loop_start()

# Inicialización Roboflow
rf = Roboflow(api_key=RF_API_KEY)
project = rf.workspace().project(MODEL_ID)
model = project.version(VERSION).model

print("🚀 Iniciando Motor de IA BroccoSort (DATASET_2)...")

while True:
    try:
        # 1. Obtener imagen remota
        respuesta = requests.get(URL_CAMARA, timeout=5)
        if respuesta.status_code == 200:
            with open("captura_temp.jpg", "wb") as f:
                f.write(respuesta.content)

            # 2. Inferencia con IA
            prediccion = model.predict("captura_temp.jpg", confidence=40, overlap=30).json()

            if "predictions" in prediccion and len(prediccion["predictions"]) > 0:
                mejor_prediccion = prediccion["predictions"][0]
                clase = mejor_prediccion["class"].lower().strip()
                confianza = mejor_prediccion["confidence"]

                print(f"🥦 [IA] Detectado: {clase.upper()} (Confianza: {confianza:.2f})")

                # 3. Lógica de control físico y envío MQTT
                angulo = 0
                if clase == "fresco":
                    angulo = 0    # Posición neutra
                elif clase == "maduro":
                    angulo = 90   # Desvío moderado
                elif clase == "podrido":
                    angulo = 180  # Desvío al contenedor de merma

                # Publicar a los tópicos industriales de 4 niveles
                cliente_mqtt.publish(TOPICO_BRAZO, str(angulo))
                
            else:
                print("⏳ [IA] Banda despejada. Esperando hortaliza...")

        # Pausa para no saturar la red ni la API
        time.sleep(2)

    except Exception as e:
        print(f"❌ Error en el pipeline de visión/red: {e}")
        time.sleep(3)
