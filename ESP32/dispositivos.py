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

from machine import Pin, ADC, PWM
import time

class SensorBox:
    """
    HAL de Sensores: Encapsula la complejidad de lectura de los sensores físicos.
    Permite obtener datos procesados sin que la lógica principal toque los pines.
    """
    def __init__(self):
        # Configuración de pines físicos
        self.disparador = Pin(5, Pin.OUT)
        self.eco = Pin(18, Pin.IN)
        self.sensor_presencia = Pin(19, Pin.IN)
        self.sensor_luz = ADC(Pin(34))
        self.sensor_luz.atten(ADC.ATTN_11DB) 

    def leer_distancia_cm(self):
        """Calcula distancia mediante pulso ultrasónico."""
        self.disparador.value(0)
        time.sleep_us(2)
        self.disparador.value(1)
        time.sleep_us(10)
        self.disparador.value(0)
        
        while self.eco.value() == 0: pass
        inicio = time.ticks_us()
        while self.eco.value() == 1: pass
        fin = time.ticks_us()
        
        duracion = time.ticks_diff(fin, inicio)
        return (duracion * 0.0343) / 2

    def hay_objeto(self):
        """Lectura digital del sensor infrarrojo de presencia."""
        return self.sensor_presencia.value() == 0

    def leer_nivel_luz(self):
        """Promedia lecturas analógicas del LDR para estabilidad."""
        suma = sum([self.sensor_luz.read() for _ in range(5)])
        return ( (suma / 5) / 4095) * 100

    def obtener_resumen_sensores(self):
        """Punto de acceso único para la lógica de comunicación MQTT."""
        return {
            "distancia": self.leer_distancia_cm(),
            "presencia": self.hay_objeto(),
            "luz": self.leer_nivel_luz()
        }

class ActuatorBox:
    """
    HAL de Actuadores: Centraliza el control de movimiento y alertas.
    Asegura que el hardware responda a comandos lógicos definidos.
    """
    def __init__(self):
        self.brazo = PWM(Pin(13), freq=50)
        self.motor_banda_a = Pin(12, Pin.OUT)
        self.motor_banda_b = Pin(14, Pin.OUT)
        self.zumbador = Pin(15, Pin.OUT)

    def mover_brazo_clasificador(self, angulo):
        """Convierte ángulos lógicos (0-180) en ciclos de trabajo PWM."""
        ciclo = int(((angulo / 180) * 97) + 26)
        self.brazo.duty(ciclo)

    def control_banda(self, encendido):
        """Gestiona el estado del Puente H para la banda transportadora."""
        val = 1 if encendido else 0
        self.motor_banda_a.value(val)
        self.motor_banda_b.value(0)

    def activar_alerta_error(self, duracion=0.5):
        """Accionamiento controlado del zumbador."""
        self.zumbador.value(1)
        time.sleep(duracion)
        self.zumbador.value(0)

    def estado_seguro(self):
        """Protocolo de seguridad para detener hardware inmediatamente."""
        self.control_banda(False)
        self.zumbador.value(0)
        self.brazo.duty(0)
