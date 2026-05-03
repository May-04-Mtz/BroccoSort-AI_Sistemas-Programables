"""
OBJETIVO: 
Implementar un sistema automatizado de clasificación de hortalizas... (Descripción completa)
INTEGRANTES: 
Mayra Paola Martínez Aranda (Código)
Nissi Sarahi Prats Ramírez (Código)
Erik Fabian Gonsalez Jimenez (Código)
PROYECTO: 
"BroccoSort AI: Sistema Automatizado de Clasificación de Hortalizas por Visión y Morfología"
"""

import paho.mqtt.client as mqtt
from datetime import datetime
import time

# Configuración del Broker
BROKER = "ip_de_tu_broker" # Ej: "192.168.1.10" o "broker.hivemq.com"
PORT = 1883

def on_connect(client, userdata, flags, rc):
    print(f"Servidor BroccoSort conectado con código: {rc}")
    # Suscribirse a toda la telemetría del ESP32
    client.subscribe("broccosort/telemetria/#")

def on_message(client, userdata, msg):
    # Requisito: Telemetría con Timestamps
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload = msg.payload.decode()
    print(f"[{timestamp}] REPORTE -> Tópico: {msg.topic} | Valor: {payload}")
    
    # Ejemplo de lógica de control remota
    if "presencia" in msg.topic and payload == "True":
        print(">>> Enviando comando de activación de banda...")
        client.publish("broccosort/comando/banda", "1")

# Inicialización del cliente
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    print("Iniciando Servidor de Monitoreo...")
    client.connect(BROKER, PORT, 60)
    client.loop_forever()
except KeyboardInterrupt:
    print("Servidor detenido por el usuario.")
