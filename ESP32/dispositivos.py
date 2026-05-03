"""
OBJETIVO: (Ej: Control de sensores y comunicación MQTT)
INTEGRANTES: (Mayra Paola Martinez Aranda - Código, Nissi Sarahi Prats Ramirez - Código, Erik Fabian Gonsalez Jimenez - Código)
PROYECTO: BroccoSort AI
"""

from machine import Pin, ADC, PWM
import time

class SensorBox:
    """
    Clase que gestiona la lectura y estabilización de los sensores del sistema.
    """
    def __init__(self):
        # Sensor Ultrasónico (Medición de tamaño/altura)
        self.disparador = Pin(5, Pin.OUT)
        self.eco = Pin(18, Pin.IN)
        
        # Sensor Infrarrojo (Detección de presencia)
        self.sensor_presencia = Pin(19, Pin.IN)
        
        # Sensor LDR (Luz ambiental para la cámara)
        self.sensor_luz = ADC(Pin(34))
        self.sensor_luz.atten(ADC.ATTN_11DB) # Rango hasta 3.3V

    def leer_distancia_cm(self):
        """
        Calcula la distancia al objeto en centímetros mediante ultrasonido.
        Devuelve: Flotante con la distancia.
        """
        self.disparador.value(0)
        time.sleep_us(2)
        self.disparador.value(1)
        time.sleep_us(10)
        self.disparador.value(0)
        
        while self.eco.value() == 0:
            pass
        inicio = time.ticks_us()
        while self.eco.value() == 1:
            pass
        fin = time.ticks_us()
        
        duracion = time.ticks_diff(fin, inicio)
        return (duracion * 0.0343) / 2

    def hay_objeto(self):
        """
        Verifica si el sensor infrarrojo detecta un brócoli frente a él.
        Devuelve: Booleano (True si hay objeto).
        """
        return self.sensor_presencia.value() == 0

    def leer_nivel_luz(self):
        """
        Lee la fotorresistencia 5 veces para estabilizar la lectura y 
        devuelve un promedio del porcentaje de brillo (0-100%).
        """
        suma = 0
        for _ in range(5):
            suma += self.sensor_luz.read()
            time.sleep_ms(10) 
        promedio = suma / 5
        return (promedio / 4095) * 100

    def obtener_resumen_sensores(self):
        """
        Genera un diccionario con las lecturas actuales de todo el hardware.
        """
        return {
            "distancia": self.leer_distancia_cm(),
            "presencia": self.hay_objeto(),
            "luz": self.leer_nivel_luz()
        }

class ActuatorBox:
    """
    Clase que controla los motores, servos y alertas sonoras.
    """
    def __init__(self):
        # Servomotor de clasificación (Pin 13)
        self.brazo = PWM(Pin(13), freq=50)
        
        # Control de la banda (Puente H)
        self.motor_banda_a = Pin(12, Pin.OUT)
        self.motor_banda_b = Pin(14, Pin.OUT)
        
        # Alerta sonora (Zumbador)
        self.zumbador = Pin(15, Pin.OUT)

    def mover_brazo_clasificador(self, angulo):
        """
        Mueve el servo a una posición específica (0, 90 o 180 grados).
        """
        ciclo = int(((angulo / 180) * 97) + 26)
        self.brazo.duty(ciclo)

    def control_banda(self, encendido):
        """
        Enciende o apaga el motor de la banda transportadora.
        """
        if encendido:
            self.motor_banda_a.value(1)
            self.motor_banda_b.value(0)
        else:
            self.motor_banda_a.value(0)
            self.motor_banda_b.value(0)

    def activar_alerta_error(self, duracion=0.5):
        """
        Hace sonar el zumbador para indicar un brócoli echado a perder.
        """
        self.zumbador.value(1)
        time.sleep(duracion)
        self.zumbador.value(0)

    def estado_seguro(self):
        """
        Detiene todos los movimientos y sonidos del sistema inmediatamente.
        """
        self.control_banda(False)
        self.zumbador.value(0)
        self.brazo.duty(0)
        print("SISTEMA EN ESTADO SEGURO")
