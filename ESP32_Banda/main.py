# ------------------------------------------------------------------
# PROYECTO: BroccoSort AI: Sistema Automatizado de Clasificación 
#           de Hortalizas por Visión y Morfología
# INTEGRANTES: 
# - Mayra Paola Martínez Aranda (22240233)
# - Nissi Sarahi Prats Ramírez (23240003)
# - Erik Fabian Gonsalez Jimenez (23240022)
# DESCRIPCIÓN:Este script constituye el nodo de ejecución física del sistema BroccoSort. 
#Su función es supervisar de forma continua los sensores perimetrales (IR, ultrasónico, LDR) y 
#traducir los comandos lógicos enviados por el servidor de visión artificial en acciones mecánicas 
#precisas sobre la banda transportadora y los indicadores de estado.
# ------------------------------------------------------------------

import machine
import sys
import time
import uselect

led_fresco = machine.Pin(15, machine.Pin.OUT)  # LED Amarillo
led_maduro = machine.Pin(27, machine.Pin.OUT)  # LED Verde
led_podrido = machine.Pin(26, machine.Pin.OUT) # LED Rojo

# Pines para el Puente H L298N (Motor de la banda)
motor_in1 = machine.Pin(21, machine.Pin.OUT)   # Controla el arranque / sentido
motor_in2 = machine.Pin(22, machine.Pin.OUT)   # Controla el sentido y freno

# Entrada Digital para la Barrera Infrarroja (IR)
sensor_ir = machine.Pin(19, machine.Pin.IN)    # Avisa si hay un objeto

# Configuración del Sensor Ultrasónico
trig = machine.Pin(12, machine.Pin.OUT)        # Pin TRIGGER
echo = machine.Pin(14, machine.Pin.IN)         # Pin ECHO

# Configuración de la Fotorresistencia LDR (Lectura Analógica)
ldr = machine.ADC(machine.Pin(34))             # Pin VOUT
ldr.atten(machine.ADC.ATTN_11DB)               # Configura rango completo de lectura (0 a 3.3V)

# Configuración del Zumbador con PWM
buzzer_pin = machine.Pin(25, machine.Pin.OUT)  # Módulo Zumbador
buzzer = machine.PWM(buzzer_pin)
buzzer.duty(0)

# Configurar el escuchador del puerto serial (sys.stdin)
poller = uselect.poll()
poller.register(sys.stdin, uselect.POLLIN)

# Variable global para registrar el último estado del sensor y evitar pitidos repetitivos
ultimo_estado_ir = 1 

def apagar_leds():
    led_fresco.value(0)
    led_maduro.value(0)
    led_podrido.value(0)

def controlar_banda(estado):
    """Define el estado de movimiento del motor de la banda: 'adelante', 'atras' o 'detener'"""
    if estado == "adelante":
        motor_in1.value(1)
        motor_in2.value(0)
    elif estado == "atras":
        motor_in1.value(0)
        motor_in2.value(1)
    else:  # detener
        motor_in1.value(0)
        motor_in2.value(0)

def emitir_tono(frecuencia, duracion):
    """Genera una nota específica variando la frecuencia del PWM"""
    try:
        buzzer.freq(frecuencia)
        buzzer.duty(512) 
        time.sleep(duracion)
        buzzer.duty(0)   
    except Exception:
        buzzer_pin.value(1)
        time.sleep(duracion)
        buzzer_pin.value(0)

def medir_distancia():
    """Calcula la distancia en centímetros usando el sensor ultrasónico"""
    trig.value(0)
    time.sleep_us(2)
    
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)
    
    timeout_start = time.ticks_us()
    while echo.value() == 0:
        if time.ticks_diff(time.ticks_us(), timeout_start) > 20000:
            return -1 
            
    t1 = time.ticks_us()
    
    while echo.value() == 1:
        if time.ticks_diff(time.ticks_us(), t1) > 20000:
            return -1
            
    t2 = time.ticks_us()
    
    duracion = time.ticks_diff(t2, t1)
    distancia_cm = duracion / 58.0
    return distancia_cm

# ─── TEST DE HARDWARE DE ARRANQUE ───
led_fresco.value(1)
led_maduro.value(1)
led_podrido.value(1)

# Prueba rápida de motor hacia adelante
controlar_banda("adelante")
time.sleep(0.2)
controlar_banda("detener")

for nota in [880, 1320, 1760]:
    emitir_tono(nota, 0.1)
    time.sleep(0.05)

apagar_leds()
print("ESP32_LISTO")

while True:
    # 1. Monitorear el Sensor Infrarrojo (Detección de paso)
    estado_actual_ir = sensor_ir.value()
    
    if estado_actual_ir == 0 and ultimo_estado_ir == 1:
        emitir_tono(1500, 0.05)
        print("Objeto detectado por sensor IR en banda.")
        
        valor_luz = ldr.read()
        distancia_medida = medir_distancia()
        
        print("--- MEDICIONES ADICIONALES ---")
        print("Nivel de luz LDR (0-4095):", valor_luz)
        if distancia_medida >= 0:
            print("Distancia Ultrasonico:", distancia_medida, "cm")
        else:
            print("Distancia Ultrasonico: Error de lectura")
        print("-------------------------------")
        
    ultimo_estado_ir = estado_actual_ir

    # 2. Revisar si llegaron comandos desde la PC por USB
    if poller.poll(0):
        linea = sys.stdin.readline()
        
        if linea:
            comando = linea.strip().lower()
            se_detecto_objeto = False
            accion_banda = "detener"
            
            if "fresco" in comando:
                apagar_leds()
                led_fresco.value(1)
                emitir_tono(2200, 0.12)
                se_detecto_objeto = True
                accion_banda = "detener"
                
            elif "maduro" in comando:
                apagar_leds()
                led_maduro.value(1)
                emitir_tono(1200, 0.15)
                se_detecto_objeto = True
                accion_banda = "atras"
                
            elif "podrido" in comando:
                apagar_leds()
                led_podrido.value(1)
                emitir_tono(450, 0.12)
                time.sleep(0.06)
                emitir_tono(350, 0.22)
                se_detecto_objeto = True
                accion_banda = "adelante"
                
            elif "ninguno" in comando:
                apagar_leds()
            
            # --- SECUENCIA DE TIEMPO PARA LA BANDA SEGÚN EL ESTADO ---
            if se_detecto_objeto:
                if accion_banda == "detener":
                    print("Fresco detectado. Deteniendo la banda inmediatamente.")
                    controlar_banda("detener")
                    time.sleep(10.0)  # Mantiene la banda detenida para revisión física
                    
                elif accion_banda == "atras":
                    print("Maduro detectado. Invirtiendo giro de la banda (Reversa)...")
                    controlar_banda("atras")
                    time.sleep(10.0)  # Despeja el objeto hacia atrás
                    controlar_banda("detener")
                    
                elif accion_banda == "adelante":
                    print("Podrido detectado. Avanzando banda de manera normal...")
                    controlar_banda("adelante")
                    time.sleep(10.0)  # Despeja el objeto hacia adelante
                    controlar_banda("detener")
                
                print("Esperando pausa reglamentaria de 10 segundos...")
                time.sleep(10.0) 
                print("Espera concluida. Sistema listo para siguiente lectura.")
                
    time.sleep(0.02)
