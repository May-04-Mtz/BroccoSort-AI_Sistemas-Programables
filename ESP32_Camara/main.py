# ------------------------------------------------------------------
# PROYECTO: BroccoSort AI: Sistema Automatizado de Clasificación 
#           de Hortalizas por Visión y Morfología
# INTEGRANTES: 
# - Mayra Paola Martínez Aranda (22240233)
# - Nissi Sarahi Prats Ramírez (23240003)
# - Erik Fabian Gonsalez Jimenez (23240022)
# OBJETIVO:Este módulo funciona como el "cerebro central" del sistema BroccoSort. 
#Su función es realizar la captura de video en tiempo real, ejecutar el pipeline de 
#inferencia para la clasificación de hortalizas y gestionar la persistencia de datos 
#en la nube (Firebase), cerrando el ciclo con el envío de comandos de control al hardware a través del puerto serie.
# ====================================================================

import cv2
import requests
import base64
import serial
import time

# ====================================================================
# 1. Configuración de la Cámara del Celular (IP Webcam)
# ====================================================================
IP_CELULAR = "192.168.200.50"  
PUERTO_APP = "8080"           

URL_CAMARA = f"http://{IP_CELULAR}:{PUERTO_APP}/video"

# ====================================================================
# Configuración del Área de Recorte (ROI - Región de Interés)
# ====================================================================
Y_INICIO = 100
Y_FIN = 600
X_INICIO = 200
X_FIN = 700

# ====================================================================
# 2. Configuración del Puerto Serial
# ====================================================================
PUERTO_COM = 'COM4'  
try:
    esp32 = serial.Serial(PUERTO_COM, 115200, timeout=1)
    time.sleep(2) 
    print(f"Conectado exitosamente al ESP32 en el puerto {PUERTO_COM}")
except Exception as e:
    print(f"Error al conectar con el puerto {PUERTO_COM}: {e}")
    esp32 = None

# ====================================================================
# 3. Configuración de Firebase Realtime Database
# ====================================================================
FIREBASE_URL = "https://broccosort-ai-default-rtdb.firebaseio.com"

# ====================================================================
# 4. Credenciales de Roboflow
# ====================================================================
ROBOFLOW_API_KEY = "Yhhcj1bdoRo0Cavl2jZV"
MODEL_ID = "broccoli-8syka-yrzti"
VERSION = "2"  

URL_API = f"https://detect.roboflow.com/{MODEL_ID}/{VERSION}?api_key={ROBOFLOW_API_KEY}&confidence=20"

print(f"[CÁMARA] Conectando a la transmisión del celular en: {URL_CAMARA}...")
cap = cv2.VideoCapture(URL_CAMARA)

print("\n--- SISTEMA LISTO ---")
print("Instrucciones:")
print("- Presiona la barra ESPACIADORA para analizar el brócoli.")
print("- Presiona la tecla 'q' para salir del programa.")

while True:
    ret, frame_completo = cap.read()
    
    if not ret:
        print("[CÁMARA] Transmisión interrumpida o búfer saturado. Intentando reconectar...")
        cap.release()
        time.sleep(2)
        cap = cv2.VideoCapture(URL_CAMARA)
        continue
    
    # Aplicar el recorte al cuadro original usando las coordenadas configuradas
    frame = frame_completo[Y_INICIO:Y_FIN, X_INICIO:X_FIN]
    
    # Mostrar únicamente el cuadro recortado enfocado en la banda
    cv2.imshow('Detector de Brocoli - IP Webcam Celular (Recortado)', frame)
    
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord(' '): 
        print("\n[INFO] Capturando imagen recortada de alta calidad...")
        
        # Codificar el cuadro RECORTADO a JPEG en memoria
        _, buffer = cv2.imencode('.jpg', frame)
        b64_img = base64.b64encode(buffer).decode('utf-8')
        
        print("[API] Enviando imagen a Roboflow...")
        headers = {'Content-Type': 'text/plain'}
        
        try:
            respuesta = requests.post(URL_API, data=b64_img, headers=headers)
            resultado = respuesta.json()
            
            if "predictions" in resultado and len(resultado["predictions"]) > 0:
                mejor_prediccion = resultado["predictions"][0]
                
                clase = mejor_prediccion["class"].strip().lower()
                confianza = mejor_prediccion["confidence"]
                
                print(f"IA DETECTO: {clase.upper()} ({confianza * 100:.2f}%)")
                
                url_historial = f"{FIREBASE_URL}/historial_json.json"
                res_get = requests.get(url_historial)
                datos_actuales = res_get.json()
                
                if datos_actuales is None:
                    siguiente_id = 0
                elif isinstance(datos_actuales, list):
                    siguiente_id = len(datos_actuales)
                else:
                    siguiente_id = len(datos_actuales)
                
                payload_firebase = {
                    "clase": clase,
                    "confianza": confianza,
                    "timestamp": int(time.time())
                }
                
                url_dest = f"{FIREBASE_URL}/historial_json/{siguiente_id}.json"
                res_fb = requests.put(url_dest, json=payload_firebase)
                
                if res_fb.status_code == 200:
                    print(f"--> Datos guardados en formato JSON en el ID [{siguiente_id}].")
                else:
                    print(f"--> Error al guardar en Firebase. Codigo: {res_fb.status_code}")
                
                if esp32:
                    esp32.write(f"{clase}\n".encode('utf-8'))
                    print(f"--> Comando enviado al puerto serie: {clase}")
            else:
                print("La IA no encontro ningun brocoli en el cuadro.")
                
                url_historial = f"{FIREBASE_URL}/historial_json.json"
                res_get = requests.get(url_historial)
                datos_actuales = res_get.json()
                
                siguiente_id = 0 if datos_actuales is None else len(datos_actuales)
                
                payload_firebase = {
                    "clase": "ninguno",
                    "confianza": 0.0,
                    "timestamp": int(time.time())
                }
                url_dest = f"{FIREBASE_URL}/historial_json/{siguiente_id}.json"
                requests.put(url_dest, json=payload_firebase)
                
                if esp32:
                    esp32.write("ninguno\n".encode('utf-8'))
                    print("--> Comando enviado al puerto serie: ninguno")
                    
        except Exception as e:
            print("Error en la peticion de red:", e)
            
    elif key == ord('q'): 
        break

cap.release()
cv2.destroyAllWindows()
if esp32:
    esp32.close()
print("Programa finalizado.")
