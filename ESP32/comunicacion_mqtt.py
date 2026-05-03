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

"""
OBJETIVO: Gestionar la conexión MQTT y los callbacks para el control de actuadores.
INTEGRANTES: Mayra Martínez, Nissi Prats, Erik González.
PROYECTO: BroccoSort AI
"""
from umqtt.simple import MQTTClient
from dispositivos import ActuatorBox
import ujson

class MQTTHandler:
    def __init__(self, broker, client_id, actuadores: ActuatorBox):
        self.client = MQTTClient(client_id, broker)
        self.actuadores = actuadores
        self.client.set_callback(self.sub_cb)

    def conectar(self):
        self.client.connect()
        self.client.subscribe(b"broccosort/comando/#")
        print("Conectado al Broker y suscrito a comandos.")

    def sub_cb(self, topic, msg):
        """Callback para procesar comandos externos"""
        print(f"Comando recibido: {topic} -> {msg}")
        
        if topic == b"broccosort/comando/brazo":
            angulo = int(msg)
            self.actuadores.mover_brazo_clasificador(angulo)
        
        elif topic == b"broccosort/comando/banda":
            estado = int(msg) == 1
            self.actuadores.control_banda(estado)
            
        elif topic == b"broccosort/comando/alerta":
            self.actuadores.activar_alerta_error()

    def publicar_telemetria(self, datos):
        for clave, valor in datos.items():
            topic = f"broccosort/telemetria/{clave}"
            self.client.publish(topic, str(valor))
