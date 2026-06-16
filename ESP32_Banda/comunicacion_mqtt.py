# ------------------------------------------------------------------
# PROYECTO: BroccoSort AI: Sistema Automatizado de Clasificación 
#           de Hortalizas por Visión y Morfología
# INTEGRANTES: 
# - Mayra Paola Martínez Aranda (22240233)
# - Nissi Sarahi Prats Ramírez (23240003)
# - Erik Fabian Gonsalez Jimenez (23240022)
# DESCRIPCIÓN:Actúa como la interfaz de comunicación de alto nivel para la gestión de eventos en tiempo real.
#Este módulo centraliza tanto la telemetría (envío de estados de sensores hacia la nube) como el control de actuadores 
#(recepción de comandos de la IA), asegurando que la ESP32 se mantenga siempre sincronizada con el estado global del sistema de clasificación.
# ------------------------------------------------------------------

import time
import ujson
from umqtt.simple import MQTTClient

class ManejadorMQTT:
    def __init__(self, servidor_broker, id_cliente, instancia_actuadores):
        self.servidor = servidor_broker
        self.id_cliente = id_cliente
        self.actuadores = instancia_actuadores
        self.cliente = MQTTClient(self.id_cliente, self.servidor)

    def conectar_nodo_central(self):
        self.cliente.set_callback(self._callback_interno)
        self.cliente.connect()
        self.cliente.subscribe(b"broccosort/brazo/banda01/actuador02")
        print("🌐 Canal MQTT en linea.")

    def verificar_mensajes_pendientes(self):
        self.cliente.check_msg()

    def publicar_disparo_presencia(self, estado_binario):
        self.cliente.publish(b"broccosort/presencia/banda01/sensor01", estado_binario.encode())

    def publicar_estado_telemetria(self, diccionario_datos):
        trama_json = ujson.dumps(diccionario_datos)
        self.cliente.publish(b"broccosort/telemetria/banda01/sensores", trama_json.encode())

    def _callback_interno(self, topico, mensaje_crudo):
        try:
            datos = ujson.loads(mensaje_crudo.decode('utf-8'))
            izq = datos["servo_izquierdo"]
            der = datos["servo_derecho"]
            color = datos["led_color"]
            alarma = datos["alerta_sonora"]
            
            self.actuadores.ejecutar_accion_clasificador(izq, der, color, alarms)
            time.sleep(1.5)
            
            self.actuadores.servomotor_izquierdo.mover_angulo(0)
            self.actuadores.servomotor_derecho.mover_angulo(0)
            self.actuadores.apagar_matriz_visual()
            self.actuadores.operar_motores_traccion(True)
        except Exception as e:
            print("Error MQTT:", e)
            self.actuadores.establecer_modo_seguro()
