# OBJETIVO:
Implementar un sistema automatizado de clasificación de hortalizas que utiliza visión artificial y sensores físicos para categorizar brócoli según su estado de madurez (color) y dimensiones (tamaño). El sistema busca optimizar la producción agrícola local mediante una banda transportadora controlada por un ESP32 S3 CAM, la cual desvía automáticamente el producto de baja calidad, emite alertas sonoras y visuales, y permite el monitoreo remoto de estadísticas de producción a través de una interfaz web y notificaciones en la nube.

# INTEGRANTES:
- Mayra Paola Martínez Aranda(22240233) 
- Nissi Sarahi Prats Ramírez(23240003) 
- Erik Fabian Gonsalez Jimenez(23240022)  

# PROYECTO:
"BroccoSort AI: Sistema Automatizado de Clasificación de Hortalizas por Visión y Morfología"

# Matriz de Tópicos MQTT - BroccoSort AI
Este documento detalla la jerarquía de comunicación entre la ESP32 y el servidor Python.

# 🗺️ Matriz de Tópicos MQTT - Estándar Industrial (4 Niveles)

Para cumplir estrictamente con la arquitectura de tópicos predecible y estandarizada exigida en el curso, y asegurar una perfecta integración con el árbol JSON NoSQL de **Firebase Realtime Database**, se reestructuraron todos los canales de comunicación bajo el formato rígido de 4 niveles:

> **Formato:** `proyecto / tipo_nodo / nombre_modulo / id_dispositivo`

## 📊 Tabla de Mapeo de Dispositivos (100% Sensores y Actuadores)

| Nivel 1: Proyecto | Nivel 2: Tipo Nodo | Nivel 3: Módulo | Nivel 4: ID Dispositivo | Dirección de Datos | Formato del Payload | Descripción Funcional |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `broccosort` | `presencia` | `banda01` | `sensor01` | ESP32 $\rightarrow$ Python | `1` o `0` | Sensor óptico/IR que detecta la hortaliza en la banda. Actúa como el disparador (trigger) asíncrono para la captura de imagen de la IA. |
| `broccosort` | `distancia` | `banda01` | `sensor02` | ESP32 $\rightarrow$ Python | `String (float)` | Telemetría en tiempo real del sensor ultrasónico en centímetros para el análisis morfológico. |
| `broccosort` | `luz` | `banda01` | `sensor03` | ESP32 $\rightarrow$ Python | `String (float)` | Lectura del sensor LDR para monitorear el nivel de iluminación ambiental y calibrar la exposición de la cámara. |
| `broccosort` | `banda` | `banda01` | `actuador01` | Python $\rightarrow$ ESP32 | `1` o `0` | Comando de control enviado desde el servidor de IA para arrancar (`1`) o parar (`0`) el motor de la banda transportadora. |
| `broccosort` | `brazo` | `banda01` | `actuador02` | Python $\rightarrow$ ESP32 | `0` / `90` / `180` | Comando de posición angular dirigido al servomotor clasificador según la inferencia de la IA (`0°` = Apto, `90°` = Media/Floración, `180°` = Rechazado/Podrido). |
| `broccosort` | `alerta` | `banda01` | `actuador03` | Python $\rightarrow$ ESP32 | `1` o `0` | Activación remota de salida digital (Zumbador/LED indicador) cuando el modelo de IA clasifica una hortaliza en estado de descomposición. |

---

## 🪵 Impacto en la Estructura NoSQL (Firebase Realtime Database)

Gracias a este esquema jerárquico de izquierda a derecha (de lo general a lo específico), la base de datos NoSQL genera un árbol JSON limpio sin duplicación de registros ni lecturas vacías:

```json
{
  "broccosort": {
    "banda01": {
      "presencia": {
        "sensor01": 1
      },
      "distancia": {
        "sensor02": "14.5"
      },
      "luz": {
        "sensor03": "85.2"
      },
      "banda": {
        "actuador01": 1
      },
      "brazo": {
        "actuador02": 180
      },
      "alerta": {
        "actuador03": 1
      }
    }
  }
}
