# BroccoSort AI: Sistema Automatizado de Clasificación de Hortalizas por Visión y Morfología

### Instituto Tecnológico de León
* **Materia:** Sistemas Programables (ISC)  
* **Profesor:** MA VERONICA TAPIA IBARRA  
* **Fecha de Entrega:** 20 de mayo de 2026  

---

## 👥 Integrantes
* Mayra Paola Martínez Aranda (22240233) 
* Nissi Sarahi Prats Ramírez (23240003) 
* Erik Fabian Gonsalez Jimenez (23240022)  

---

## 🎯 Objetivo del Proyecto
Implementar un sistema automatizado de clasificación de hortalizas que utiliza visión artificial y sensores físicos para categorizar brócoli según su estado de madurez (color) y dimensiones (tamaño). El sistema busca optimizar la producción agrícola local mediante una banda transportadora controlada por un ESP32 S3 CAM, la cual desvía automáticamente el producto de baja calidad, emite alertas sonoras y visuales, y permite el monitoreo remoto de estadísticas de producción a través de una interfaz web y notificaciones en la nube.

---

## 📂 Estructura del Repositorio y Módulos

El ecosistema de software se encuentra completamente desacoplado y estructurado de la siguiente forma para cumplir con los estándares de diseño modular:

### 🎛️ Modulo ESP32 (Firmware Local)
* **`main.py` / `firmware_control.py`**: Nodo de ejecución física. Supervisa continuamente los sensores perimetrales (IR, ultrasónico, LDR) y traduce los comandos lógicos enviados por el servidor de visión artificial en acciones mecánicas precisas sobre la banda transportadora a través del puente H L298N.
* **`dispositivos.py`**: Capa de Abstracción de Hardware (HAL) que define y encapsula las clases para la gestión de periféricos, aislando los pines físicos de la lógica de comunicación.

### 🖥️ Módulos de Servidor (Python Central)
* **`DATASET_2.py`**: Orquestador de Visión Artificial. Realiza la captura de video en tiempo real mediante un área de recorte controlada (ROI), ejecuta el pipeline de inferencia con el SDK de Roboflow y publica las decisiones de control hacia la red MQTT.
* **`servidor_broccosort.py`**: Backend Logger del Sistema. Actúa como puente entre la red local y la nube; se suscribe a los tópicos de control, procesa las métricas de rendimiento y persiste los registros en Firebase en un formato JSON incremental indexado.

---

## 🌐 Matriz de Tópicos MQTT - Estándar Industrial (4 Niveles)

Para garantizar un diseño predecible y estandarizado, se ha implementado un formato rígido de 4 niveles en todo el ecosistema. Esto previene rutas libres o ambiguas que causen lecturas cruzadas en el sistema.

**Jerarquía Estándar:** `proyecto / tipo_nodo / nombre_modulo / id_dispositivo`

| Nivel 1: Proyecto | Nivel 2: Tipo Nodo | Nivel 3: Módulo | Nivel 4: ID Disp. | Dirección de Datos | Formato | Descripción Técnica |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `broccosort` | `presencia` | `banda01` | `sensor01` | ESP32 → Py | `1` o `0` | Trigger óptico/IR perimetral para captura e inicio del pipeline de IA. |
| `broccosort` | `distancia` | `banda01` | `sensor02` | ESP32 → Py | `String` | Telemetría ultrasónica para la adquisición de dimensiones de la hortaliza. |
| `broccosort` | `luz` | `banda01` | `sensor03` | ESP32 → Py | `String` | Nivel LDR para la calibración lumínica del entorno de visión. |
| `broccosort` | `banda` | `banda01` | `actuador01` | Py → ESP32 | `1` o `0` | Comando de control para el arranque (`1`) y paro (`0`) del motor de la banda. |
| `broccosort` | `brazo` | `banda01` | `actuador02` | Py → ESP32 | `0` / `90` / `180` | Posición angular del servo clasificador según la inferencia de calidad de la IA. |
| `broccosort` | `alerta` | `banda01` | `actuador03` | Py → ESP32 | `1` o `0` | Activación remota del indicador acústico (Zumbador) ante producto podrido. |

---

## ☁️ Mapeo Estructurado en Firebase Realtime Database (NoSQL)

Al mover los tópicos de lo general a lo específico de izquierda a derecha separados por diagonales (`/`), las colecciones NoSQL en la nube se estructuran de forma nativa en un árbol JSON limpio, garantizando una sincronización perfecta con el Dashboard:

```json
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
