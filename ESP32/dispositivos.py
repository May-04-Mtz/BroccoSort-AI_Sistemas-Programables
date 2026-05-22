# NOMBRE DEL PROYECTO: BroccoSort AI
# INTEGRANTES: Mayra Paola Martinez Aranda, Nissi Sarahi Prats Ramirez, Erik Fabian Gonsalez Jimenez
# DESCRIPCIÓN: Biblioteca HAL optimizada con filtrado antirrebote y calibración dinámica de servo.

from machine import Pin, ADC, PWM
import time

class SensorBox:
    """Gestiona la lectura y estabilización de los sensores del sistema."""
    def __init__(self):
        # Sensor Ultrasónico (Trigger: Pin 5, Echo: Pin 18)
        self.disparador = Pin(5, Pin.OUT)
        self.eco = Pin(18, Pin.IN)
        
        # Sensor Infrarrojo
        self.sensor_presencia = Pin(19, Pin.IN)
        
        # Sensor LDR
        self.sensor_luz = ADC(Pin(34))
        self.sensor_luz.atten(ADC.ATTN_11DB) 

    def leer_distancia_cm(self):
        lecturas = []
        for _ in range(5):
            self.disparador.value(0)
            time.sleep_us(2)
            self.disparador.value(1)
            time.sleep_us(10)
            self.disparador.value(0)
            
            inicio_timeout = time.ticks_us()
            while self.eco.value() == 0:
                if time.ticks_diff(time.ticks_us(), inicio_timeout) > 30000:
                    return -1  
            
            inicio = time.ticks_us()
            while self.eco.value() == 1:
                if time.ticks_diff(time.ticks_us(), inicio_timeout) > 30000:
                    return -1  
            
            fin = time.ticks_us()
            duracion = time.ticks_diff(fin, inicio)
            distancia = (duracion * 0.0343) / 2
            lecturas.append(distancia)
            time.sleep_ms(10) 
            
        return sum(lecturas) / len(lecturas)

    def hay_objeto(self):
        """Filtrado digital antirrebote (40ms totales)."""
        for _ in range(8): 
            if self.sensor_presencia.value() != 0:
                return False 
            time.sleep_ms(5) 
        return True 

    def leer_nivel_luz(self):
        suma = 0
        for _ in range(5):
            suma += self.sensor_luz.read()
            time.sleep_ms(10) 
        promedio = suma / 4095
        return promedio * 100

    def obtener_resumen_sensores(self):
        return {
            "distancia": self.leer_distancia_cm(),
            "presencia": self.hay_objeto(),
            "luz": self.leer_nivel_luz()
        }

class ActuatorBox:
    """Controla los motores, servos, zumbador y LEDs indicadores."""
    def __init__(self):
        self.brazo = PWM(Pin(13), freq=50)
        self.MIN_DUTY = 26  
        self.RANGO_DUTY = 97 
        
        self.motor_banda_a = Pin(12, Pin.OUT)
        self.motor_banda_b = Pin(14, Pin.OUT)
        self.zumbador = Pin(15, Pin.OUT)
        
        self.led_verde = Pin(2, Pin.OUT)
        self.led_amarillo = Pin(4, Pin.OUT)
        self.led_rojo = Pin(33, Pin.OUT)
        self.apagar_leds()

    def mover_brazo_clasificador(self, angulo):
        ciclo = int(((angulo / 180) * self.RANGO_DUTY) + self.MIN_DUTY)
        self.brazo.duty(ciclo)
        
        if angulo == 0:       
            self.fijar_leds(verde=True)
        elif angulo == 90:    
            self.fijar_leds(amarillo=True)
        elif angulo == 180:   
            self.fijar_leds(rojo=True)
        else:                 
            self.apagar_leds()

    def control_banda(self, encendido):
        if encendido:
            self.motor_banda_a.value(1)
            self.motor_banda_b.value(0)
        else:
            self.motor_banda_a.value(0)
            self.motor_banda_b.value(0)

    def activar_alerta_error(self, duracion=0.5):
        self.zumbador.value(1)
        time.sleep(duracion)
        self.zumbador.value(0)

    def fijar_leds(self, verde=False, amarillo=False, rojo=False):
        self.led_verde.value(1 if verde else 0)
        self.led_amarillo.value(1 if amarillo else 0)
        self.led_rojo.value(1 if rojo else 0)

    def apagar_leds(self):
        self.led_verde.value(0)
        self.led_amarillo.value(0)
        self.led_rojo.value(0)

    def estado_seguro(self):
        self.control_banda(False)
        self.zumbador.value(0)
        self.apagar_leds()
        self.mover_brazo_clasificador(0) 
        self.brazo.duty(0) 
        print("🚨 SISTEMA EN ESTADO SEGURO")
