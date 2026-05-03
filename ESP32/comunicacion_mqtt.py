"""
OBJETIVO:
Implementar un sistema automatizado de clasificación de hortalizas que utiliza visión artificial 
y sensores físicos para categorizar brócoli según su estado de madurez (color) y dimensiones (tamaño). 
El sistema busca optimizar la producción agrícola local mediante una banda transportadora 
controlada por un ESP32 S3 CAM, la cual desvía automáticamente el producto de baja calidad, 
emite alertas sonoras y visuales, y permite el monitoreo remoto de estadísticas de producción 
a través de una interfaz web y notificaciones en la nube.

INTEGRANTES:
- Mayra Paola Martínez Aranda (22240233) 
- Nissi Sarahi Prats Ramírez (23240003) 
- Erik Fabian Gonsalez Jimenez (23240022)  

PROYECTO:
"BroccoSort AI: Sistema Automatizado de Clasificación de Hortalizas por Visión y Morfología"
"""

from umqtt.simple import MQTTClient
from dispositivos import ActuatorBox
import ujson

class MQTTHandler:
    def __init__(self, broker, client_id, actuadores: ActuatorBox):
        self.client = MQTTClient(client_id, broker)
        # Se recibe la instancia de la HAL (ActuatorBox) para interactuar con el hardware
        # sin acceder directamente a los pines desde esta clase.
        self.actuadores = actuadores
        # Definición del método callback que se ejecutará al recibir mensajes suscritos.
        self.client.set_callback(self.sub_cb)

    def conectar(self):
        """Establece conexión y se suscribe a la jerarquía de comandos."""
        self.client.connect()
        self.client.subscribe(b"broccosort/comando/#")
        print("Conectado al Broker y suscrito a comandos.")

    def sub_cb(self, topic, msg):
        """
        CALLBACK DE SUSCRIPCIÓN: 
        Esta función actúa como el puente entre la red (MQTT) y el hardware (HAL).
        Analiza el tópico recibido y delega la ejecución física a la clase ActuatorBox.
        """
        print(f"Comando recibido: {topic} -> {msg}")
        
        # Integración HAL: Control del ángulo del servomotor clasificador
        if topic == b"broccosort/comando/brazo":
            angulo = int(msg)
            # Se invoca la HAL para mover el servo sin configurar PWM aquí.
            self.actuadores.mover_brazo_clasificador(angulo)
        
        # Integración HAL: Control de encendido/apagado de la banda transportadora
        elif topic == b"broccosort/comando/banda":
            estado = int(msg) == 1
            # Se delega el manejo del Puente H a la función control_banda de la HAL.
            self.actuadores.control_banda(estado)
            
        # Integración HAL: Activación de señales sonoras de alerta
        elif topic == b"broccosort/comando/alerta":
            # La lógica del tiempo y estado del pin del buzzer está encapsulada en la HAL.
            self.actuadores.activar_alerta_error()

    def publicar_telemetria(self, datos):
        """
        Transforma el diccionario de datos de la HAL en mensajes MQTT individuales.
        Asegura el desacoplamiento: el hardware lee datos, esta función los comunica.
        """
        for clave, valor in datos.items():
            topic = f"broccosort/telemetria/{clave}"
            self.client.publish(topic, str(valor))
