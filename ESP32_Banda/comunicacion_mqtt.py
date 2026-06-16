# ------------------------------------------------------------------
# PROYECTO: BroccoSort AI: Sistema Automatizado de Clasificación 
#           de Hortalizas por Visión y Morfología
# INTEGRANTES: 
# - Mayra Paola Martínez Aranda (22240233)
# - Nissi Sarahi Prats Ramírez (23240003)
# - Erik Fabian Gonsalez Jimenez (23240022)
# DESCRIPCIÓN:Implementar una capa de comunicación industrial basada en el protocolo MQTT, diseñada bajo el estándar 
#de jerarquía de 4 niveles (proyecto/tipo_nodo/nombre_modulo/id_dispositivo). Este módulo garantiza que el intercambio 
#de datos sea predecible, determinista y totalmente compatible con la estructura NoSQL de Firebase.
# ------------------------------------------------------------------

from umqtt.simple import MQTTClient
from dispositivos import ActuatorBox

class MQTTHandler:
    def __init__(self, broker, client_id, actuadores: ActuatorBox):
        self.client = MQTTClient(client_id, broker)
        self.actuadores = actuadores
        self.client.set_callback(self.sub_cb)
        
# Definición estricta de tópicos de control (Jerarquía de 4 niveles NoSQL)
self.TOPICO_BANDA = b"broccosort/banda/banda01/actuador01"
self.TOPICO_BRAZO = b"broccosort/brazo/banda01/actuador02"
self.TOPICO_ALERTA = b"broccosort/alerta/banda01/actuador03"

    def conectar(self):
        """Establece conexión y se suscribe individualmente a los tópicos estructurados."""
        self.client.connect()
        # Nos suscribimos uno a uno para evitar el uso de '#' que rompe la predictibilidad del árbol NoSQL
        self.client.subscribe(self.TOPICO_BANDA)
        self.client.subscribe(self.TOPICO_BRAZO)
        self.client.subscribe(self.TOPICO_ALERTA)
        print("✅ [MQTT] Conectado al Broker y suscrito a la jerarquía formal de 4 niveles.")

    def sub_cb(self, topic, msg):
        """
        CALLBACK DE SUSCRIPCIÓN HAL:
        Mapea las solicitudes de la red directamente a las acciones físicas encapsuladas.
        """
        dato = msg.decode()
        print(f"📩 Comando recibido [{topic.decode()}]: {dato}")
        
        if topic == self.TOPICO_BRAZO:
            angulo = int(dato)
            self.actuadores.mover_brazo_clasificador(angulo)
            if angulo == 180:   
                self.actuadores.activar_alerta_error(0.6)
            elif angulo == 90:  
                self.actuadores.activar_alerta_error(0.15)
        
        elif topic == self.TOPICO_BANDA:
            estado = int(dato) == 1
            self.actuadores.control_banda(estado)
            if not estado:
                self.actuadores.estado_seguro()
                
        elif topic == self.TOPICO_ALERTA:
            self.actuadores.activar_alerta_error()

    def publicar_telemetria(self, datos):
        """
        Mapea dinámicamente las claves del diccionario HAL hacia el estándar NoSQL.
        Ejemplo: 'presencia' -> 'broccosort/banda01/presencia/sensor01'
        """
        # Mapeo explícito para garantizar el id_alfanumerico en el cuarto nivel
mapeo_topicos = {
    "presencia": "broccosort/presencia/banda01/sensor01",
    "distancia": "broccosort/distancia/banda01/sensor02",
    "luz": "broccosort/luz/banda01/sensor03"
}
        
        for clave, valor in datos.items():
            if clave in mapeo_topicos:
                topic = mapeo_topicos[clave]
                # Conversión limpia a String antes del envío
                if clave == "presencia":
                    payload = "1" if valor else "0"
                elif clave == "distancia":
                    payload = "{:.1f}".format(valor)
                else:
                    payload = "{:.1f}".format(valor)
                    
                self.client.publish(topic, payload)
