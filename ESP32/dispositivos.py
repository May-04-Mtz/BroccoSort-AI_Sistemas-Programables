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
    Clase que gestiona la lectura y estabilización de los sensores del sistema.
    """
    def __init__(self):
        # Sensor Ultrasónico (Medición de tamaño/altura)
        # Trigger: Pin 5, Echo: Pin 18
        self.disparador = Pin(5, Pin.OUT)
        self.eco = Pin(18, Pin.IN)
        
        # Sensor Infrarrojo (Detección de presencia)
        self.sensor_presencia = Pin(19, Pin.IN)
        
        # Sensor LDR (Luz ambiental para la cámara)
        self.sensor_luz = ADC(Pin(34))
        self.sensor_luz.atten(ADC.ATTN_11DB) # Rango hasta 3.3V

    def leer_distancia_cm(self):
        """
        Calcula la distancia promediando 5 lecturas para eliminar ruido.
        """
        lecturas = []
        for _ in range(5):
            self.disparador.value(0)
            time.sleep_us(2)
            self.disparador.value(1)
            time.sleep_us(10)
            self.disparador.value(0)
            
            # Timeout para evitar bucles infinitos si el sensor falla
            timeout = time.ticks_us() + 30000
            while self.eco.value() == 0 and time.ticks_us() < timeout:
                pass
            inicio = time.ticks_us()
            
            while self.eco.value() == 1 and time.ticks_us() < timeout:
                pass
            fin = time.ticks_us()
            
            duracion = time.ticks_diff(fin, inicio)
            distancia = (duracion * 0.0343) / 2
            lecturas.append(distancia)
            time.sleep_ms(10) 
            
        return sum(lecturas) / len(lecturas)

    def hay_objeto(self):
        """
        Verifica si el sensor infrarrojo detecta un brócoli.
        """
        return self.sensor_presencia.value() == 0

    def leer_nivel_luz(self):
        """
        Promedia el porcentaje de brillo (0-100%).
        """
        suma = 0
        for _ in range(5):
            suma += self.sensor_luz.read()
            time.sleep_ms(10) 
        promedio = suma / 5
        return (promedio / 4095) * 100

    def obtener_resumen_sensores(self):
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
        Mueve el servo a una posición (0 a 180).
        """
        # Fórmula para mapear grados a duty de MicroPython (aprox 26-123)
        ciclo = int(((angulo / 180) * 97) + 26)
        self.brazo.duty(ciclo)

    def control_banda(self, encendido):
        """
        Enciende o apaga el motor de la banda.
        """
        if encendido:
            self.motor_banda_a.value(1)
            self.motor_banda_b.value(0)
        else:
            self.motor_banda_a.value(0)
            self.motor_banda_b.value(0)

    def activar_alerta_error(self, duracion=0.5):
        """
        Hace sonar el zumbador.
        """
        self.zumbador.value(1)
        time.sleep(duracion)
        self.zumbador.value(0)

    def estado_seguro(self):
        """
        Detiene todo el sistema inmediatamente.
        """
        self.control_banda(False)
        self.zumbador.value(0)
        self.mover_brazo_clasificador(0) 
        self.brazo.duty(0) # Apaga PWM para evitar zumbido en el servo
        print("🚨 SISTEMA EN ESTADO SEGURO")
