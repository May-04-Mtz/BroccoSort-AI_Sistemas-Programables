"""
NOMBRE DEL PROYECTO: BroccoSort AI: Sistema Automatizado de Clasificación
de Hortalizas por Visión y Morfología
OBJETIVO: Integración de IA para Captura remota y transmisión de imágenes
de hortalizas hacia el servidor central de IA.
INTEGRANTES: 
- Mayra Paola Martínez Aranda (22240233)
- Nissi Sarahi Prats Ramírez (23240003)
- Erik Fabian Gonsalez Jimenez (23240022)
"""

import camera  # Para controlar la cámara
import network # Para conectarse a Wi-Fi
import socket  # Para crear un servidor web
import time    # Para manejar pausas

# ==========================================
# PASO 1: Conexión a la red Wi-Fi con IP Estática
# ==========================================
def conectar_wifi(ssid, password):
    """Función para conectarse a una red Wi-Fi configurando una IP fija predecible."""
    wlan = network.WLAN(network.STA_IF) 
    
    wlan.active(False)  
    time.sleep(0.5)     
    
    wlan.active(True) 
    
    # FORZAR IP ESTÁTICA: (IP_Deseada, Máscara_Subred, Puerta_Enlace, DNS)
    # Esto asegura que siempre levante en la IP que espera DATASET_2.py
    try:
        wlan.ifconfig(('192.168.8.27', '255.255.255.0', '192.168.8.1', '8.8.8.8'))
    except Exception as e:
        print("⚠️ No se pudo asignar IP estática, se usará DHCP:", e)

    wlan.connect(ssid, password)
    print('Conectando a la red Wi-Fi: %s...' % ssid)
    
    intentos = 0
    while not wlan.isconnected(): 
        time.sleep(1)
        print('.', end="") 
        intentos += 1
        if intentos > 20:
            print('\n No se pudo conectar. Verifica credenciales o energía.')
            return None
        
    print('\n¡Conexión exitosa!')
    print('Dirección IP asignada formalmente:', wlan.ifconfig()[0]) 
    return wlan.ifconfig()[0]

# ==========================================
# PASO 2: Inicializar la cámara
# ==========================================
def inicializar_camara():
    """Función para inicializar la cámara con pines estándar de Freenove WROVER."""
    try:
        camera.init(0, format=camera.JPEG, 
                    d0=4, d1=5, d2=18, d3=19, d4=36, d5=39, d6=34, d7=35,
                    href=23, vsync=25, reset=-1, pwdn=-1,
                    xclk=21, pclk=22, siod=26, sioc=27)
                    
        camera.framesize(camera.FRAME_240X240)
        print('Cámara inicializada correctamente. Esperando estabilización...')
        time.sleep(2) 
        
        # Disparo de calentamiento oculto
        camera.capture() 
        print('Sensor listo.')
        
    except Exception as e:
        print('Error al inicializar la cámara:', e)

# ==========================================
# PASO 3: Tomar una foto
# ==========================================
def tomar_foto():
    """Función para capturar una foto con la cámara."""
    print('Tomando una foto...')
    try:
        foto = camera.capture() 
        if foto: 
            print('Foto tomada exitosamente.')
            return foto
        else:
            print('Fallo interno: El sensor no devolvió datos de imagen.')
            return None
    except Exception as e:
        print('Error al tomar the foto (Excepción de Python):', e)
        return None
    
# ==========================================
# PASO 4: Configurar el servidor web
# ==========================================
def iniciar_servidor(ip):
    """Función para iniciar el servidor web HTTP optimizado para el script DATASET_2.py."""
    addr = (ip, 80) 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    
    # Línea de seguridad para reutilizar el puerto inmediatamente si se cae el servidor
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    s.bind(addr) 
    s.listen(1) 
    
    print('Servidor web iniciado listo en: http://%s' % ip)
    
    while True:
        conn, addr = s.accept() 
        print('\nConexión desde:', addr)
        try:
            request = conn.recv(1024) 
            
            if len(request) == 0:
                continue
                
            if b'GET /foto' in request:
                foto = tomar_foto() 
                if foto:
                    # Cabeceras HTTP estándar para transferencia binaria de imágenes
                    conn.send(b'HTTP/1.1 200 OK\r\n') 
                    conn.send(b'Content-Type: image/jpeg\r\n')
                    conn.send(b'Content-Length: ' + str(len(foto)).encode() + b'\r\n')
                    conn.send(b'Connection: close\r\n\r\n')
                    
                    # Envío del flujo binario completo
                    conn.sendall(foto) 
                else:
                    conn.send(b'HTTP/1.1 500 Internal Server Error\r\n')
                    conn.send(b'Content-Type: text/html\r\n\r\n')
                    conn.send(b'<html><body><h1>Error al tomar la foto</h1></body></html>')
            else:
                conn.send(b'HTTP/1.1 200 OK\r\n')
                conn.send(b'Content-Type: text/html\r\n\r\n')
                conn.send(b'<html><body>')
                conn.send(b'<h1>BroccoSort AI - Servidor ESP32-CAM</h1>')
                conn.send(b'<p>Ir a <a href="/foto">/foto</a> para capturar hortaliza.</p>')
                conn.send(b'</body></html>')
        except Exception as e:
            print('Error procesando la petición:', e)
        finally:
            conn.close() # Se cierra la conexión inmediatamente para liberar memoria RAM en la placa

# ==========================================
# PROGRAMA PRINCIPAL
# ==========================================
if __name__ == '__main__':
    # Credenciales del proyecto
    ssid = 'Nexus' 
    password = 'Hatsune.Miku.01'
    
    ip = conectar_wifi(ssid, password)
    
    if ip:
        inicializar_camara()
        iniciar_servidor(ip)
