# ------------------------------------------------------------------
# PROYECTO: BroccoSort AI: Sistema Automatizado de Clasificación 
#           de Hortalizas por Visión y Morfología
# INTEGRANTES: 
# - Mayra Paola Martínez Aranda (22240233)
# - Nissi Sarahi Prats Ramírez (23240003)
# - Erik Fabian Gonsalez Jimenez (23240022)
# OBJETIVO:Actúa como la interfaz de comunicación de alto nivel para la gestión de eventos en tiempo real.
#Este módulo centraliza tanto la telemetría (envío de estados de sensores hacia la nube) como el control de actuadores 
#(recepción de comandos de la IA), asegurando que la ESP32 se mantenga siempre sincronizada con el estado global del sistema de clasificación.
# ------------------------------------------------------------------

from machine import Pin, ADC, PWM
import time

class Servomotor:
    def __init__(self, pin_salida, frecuencia=50, ciclo_minimo=26, ciclo_maximo=123):
        self.pulso_modulado = PWM(Pin(pin_salida), freq=frecuencia)
        self.ciclo_minimo = ciclo_minimo
        self.rango_ciclo = ciclo_maximo - ciclo_minimo

    def mover_angulo(self, angulo_grados):
        if angulo_grados < 0: angulo_grados = 0
        if angulo_grados > 180: angulo_grados = 180
        calculo_ciclo = int(((angulo_grados / 180) * self.rango_ciclo) + self.ciclo_minimo)
        self.pulso_modulado.duty(calculo_ciclo)

    def desactivar_pulso(self):
        self.pulso_modulado.duty(0)


class CajaSensores:
    def __init__(self):
        self.disparador_pulso = Pin(12, Pin.OUT)
        self.eco_pulso = Pin(14, Pin.IN)
        self.barrera_infrarrojo = Pin(19, Pin.IN)
        self.conversor_luminosidad = ADC(Pin(34))
        self.conversor_luminosidad.atten(ADC.ATTN_11DB) 

    def leer_distancia_cm(self):
        muestras = []
        for _ in range(3):
            self.disparador_pulso.value(0)
            time.sleep_us(2)
            self.disparador_pulso.value(1)
            time.sleep_us(10)
            self.disparador_pulso.value(0)
            
            limite = time.ticks_us()
            while self.eco_pulso.value() == 0:
                if time.ticks_diff(time.ticks_us(), limite) > 20000: return -1.0
            
            inicio = time.ticks_us()
            while self.eco_pulso.value() == 1:
                if time.ticks_diff(time.ticks_us(), limite) > 20000: return -1.0
            
            duracion = time.ticks_diff(time.ticks_us(), inicio)
            muestras.append((duracion * 0.0343) / 2)
            time.sleep_ms(5)
        return sum(muestras) / len(muestras) if muestras else -1.0

    def comprobar_presencia_objeto(self):
        for _ in range(5): 
            if self.barrera_infrarrojo.value() != 0: return False 
            time.sleep_ms(4) 
        return True 

    def leer_porcentaje_luz(self):
        suma = 0
        for _ in range(4):
            suma += self.conversor_luminosidad.read()
            time.sleep_ms(5)
        return ((suma / 4) / 4095) * 100

    def generar_reporte_variables(self):
        return {
            "distancia_cm": self.leer_distancia_cm(),
            "objeto_presente": self.comprobar_presencia_objeto(),
            "porcentaje_iluminacion": self.leer_porcentaje_luz()
        }


class CajaActuadores:
    def __init__(self):
        # Mapeo físico validado sin colisiones con la cámara
        self.servomotor_izquierdo = Servomotor(pin_salida=2)  # Servo Desviador 1 (Fresco)
        self.servomotor_derecho = Servomotor(pin_salida=4)    # Servo Desviador 2 (Maduro)
        
        # --- MODIFICADO: Conexiones del Puente H L298N con control PWM de Velocidad ---
        # Configuramos el pin 21 como PWM a 1000Hz para poder regular su potencia
        self.pista_motor_a = PWM(Pin(21), freq=1000)
        self.pista_motor_b = Pin(22, Pin.OUT)
        
        # Matriz de LEDs e Indicador Acústico de 3 pines
        self.led_indicador_amarillo = Pin(15, Pin.OUT)
        self.led_indicador_verde = Pin(27, Pin.OUT)
        self.led_indicador_rojo = Pin(26, Pin.OUT)
        self.pin_buzzer_io = Pin(25, Pin.OUT)  
        
        self.apagar_matriz_visual()

    def operar_motores_traccion(self, estado_marcha):
        """Controla el encendido, apagado y la velocidad física de la banda."""
        if estado_marcha:
            # En MicroPython el rango de PWM va de 0 (detenido) a 1023 (máxima velocidad).
            # Cambia el valor 650 para ajustar la velocidad a tu gusto:
            # 550 = Muy Lento | 650 = Lento Moderado | 800 = Rápido | 1023 = Máxima velocidad
            self.pista_motor_a.duty(650) 
            self.pista_motor_b.value(0)
        else:
            self.pista_motor_a.duty(0)   
            self.pista_motor_b.value(0)

    def ejecutar_accion_clasificador(self, angulo_izq, angulo_der, color_led, activar_alarma):
        """Mueve los servos de compuerta de manera coordinada."""
        self.servomotor_izquierdo.mover_angulo(angulo_izq)
        self.servomotor_derecho.mover_angulo(angulo_der)
        
        self.apagar_matriz_visual()
        if color_led == "amarillo": self.led_indicador_amarillo.value(1)
        elif color_led == "verde": self.led_indicador_verde.value(1)
        elif color_led == "rojo": self.led_indicador_rojo.value(1)

        if activar_alarma:
            # Pulso digital al pin I/O del módulo de 3 pines
            self.pin_buzzer_io.value(1)
            time.sleep(0.5)
            self.pin_buzzer_io.value(0)

    def apagar_matriz_visual(self):
        self.led_indicador_verde.value(0)
        self.led_indicador_amarillo.value(0)
        self.led_indicador_rojo.value(0)

    def establecer_modo_seguro(self):
        self.operar_motores_traccion(False)
        self.pin_buzzer_io.value(0)
        self.apagar_matriz_visual()
        self.servomotor_izquierdo.desactivar_pulso()
        self.servomotor_derecho.desactivar_pulso()
