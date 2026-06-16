# OBJETIVO:
Implementar un sistema automatizado de clasificación de hortalizas que utiliza visión artificial y sensores físicos para categorizar brócoli según su estado de madurez (color) y dimensiones (tamaño). El sistema busca optimizar la producción agrícola local mediante una banda transportadora controlada por un ESP32 S3 CAM, la cual desvía automáticamente el producto de baja calidad, emite alertas sonoras y visuales, y permite el monitoreo remoto de estadísticas de producción a través de una interfaz web y notificaciones en la nube.

# INTEGRANTES:
- Mayra Paola Martínez Aranda(22240233) 
- Nissi Sarahi Prats Ramírez(23240003) 
- Erik Fabian Gonsalez Jimenez(23240022)  

# PROYECTO:
"BroccoSort AI: Sistema Automatizado de Clasificación de Hortalizas por Visión y Morfología"

# Matriz de Tópicos MQTT - Estándar Industrial (4 Niveles)
### 1. Arquitectura de Tópicos MQTT (4 Niveles)
Para cumplir con el diseño de una arquitectura de tópicos predecible y estandarizada, se ha implementado un formato rígido de 4 niveles en todo el ecosistema. Esto garantiza una sincronización perfecta con la estructura NoSQL de Firebase Realtime Database.

#### Tabla de Mapeo del Ecosistema IoT

| Nivel 1: Proyecto | Nivel 2: Tipo Nodo | Nivel 3: Módulo | Nivel 4: ID Disp. | Dirección de Datos | Formato | Descripción Técnica |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `broccosort` | `presencia` | `banda01` | `sensor01` | ESP32 $\rightarrow$ Py | `1` o `0` | Trigger óptico/IR perimetral para captura e inicio del pipeline de IA. |
| `broccosort` | `distancia` | `banda01` | `sensor02` | ESP32 $\rightarrow$ Py | `String` | Telemetría ultrasónica para la adquisición de dimensiones de la hortaliza. |
| `broccosort` | `luz` | `banda01` | `sensor03` | ESP32 $\rightarrow$ Py | `String` | Nivel LDR para la calibración lumínica del entorno de visión. |
| `broccosort` | `banda` | `banda01` | `actuador01` | Py $\rightarrow$ ESP32 | `1` o `0` | Comando de control para el arranque (`1`) y paro (`0`) del motor de la banda. |
| `broccosort` | `brazo` | `banda01` | `actuador02` | Py $\rightarrow$ ESP32 | `0` / `90` / `180` | Posición angular del servo clasificador según la inferencia de calidad de la IA. |
| `broccosort` | `alerta` | `banda01` | `actuador03` | Py $\rightarrow$ ESP32 | `1` o `0` | Activación remota del indicador acústico (Zumbador) ante producto podrido. |

---

## Mapeo Estructurado en Firebase Realtime Database (NoSQL)

Al organizar los tópicos moviéndose de lo general a lo específico de izquierda a derecha separados por diagonales (`/`), las colecciones NoSQL en la nube se estructuran de forma nativa en un árbol JSON limpio. Esto previene rutas libres o ambiguas que causen lecturas vacías o cruzadas en el Dashboard:

{
  "broccosort": {
    "presencia": {
      "banda01": {
        "sensor01": 1
      }
    },
    "distancia": {
      "banda01": {
        "sensor02": "14.5"
      }
    },
    "luz": {
      "banda01": {
        "sensor03": "78.2"
      }
    },
    "banda": {
      "banda01": {
        "actuador01": 1
      }
    },
    "brazo": {
      "banda01": {
        "actuador02": 180
      }
    },
    "alerta": {
      "banda01": {
        "actuador03": 0
      }
    },
    "historico": {
      "1781479682": {
        "clase": "podrido",
        "confianza": 0.94,
        "sensor_ir": "activo"
      },
      "1781479700": {
        "clase": "fresco",
        "confianza": 0.98,
        "sensor_ir": "activo"
      }
    }
  }
}
