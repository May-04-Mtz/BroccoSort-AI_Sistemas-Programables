from roboflow import Roboflow
import os

# 1. Configuración de tu modelo (Usando tus datos de la captura)
# El Model ID es: broccoli-6n3ht-ininr y la versión es la 3
rf = Roboflow(api_key="T5jPuaVg9YZzFQq277bt")
project = rf.workspace().project("broccoli-6n3ht-ininr")
model = project.version(3).model

# 2. Función para clasificar una foto
def clasificar_vegetal(ruta_imagen):
    print(f"Analizando: {ruta_imagen}...")
    
    # Hacemos la predicción (Ajustamos confianza a 25% para empezar)
    prediction = model.predict(ruta_imagen, confidence=25).json()
    
    if len(prediction['predictions']) > 0:
        for det in prediction['predictions']:
            clase = det['class']
            confianza = det['confidence']
            print(f"✅ RESULTADO: {clase} ({confianza*100:.1f}%)")
            
            # Aquí va tu lógica para activar motores
            if clase == "podrido":
                print("🚨 ACTIVANDO ACTUADOR: Brócoli no apto.")
    else:
        print("❓ No se detectó nada claro.")

# 3. Prueba rápida
# Asegúrate de tener una imagen llamada 'test.jpg' en la misma carpeta que este script
if os.path.exists("test.jpg"):
    clasificar_vegetal("test.jpg")
else:
    print("Sube una imagen llamada 'test.jpg' para probar.")
