# Esquema de Hardware y Conexiones Eléctricas — BroccoSort AI

### Instituto Tecnológico de León
* **Materia:** Sistemas Programables (ISC)  
* **Proyecto:** BroccoSort AI: Sistema Automatizado de Clasificación de Hortalizas por Visión y Morfología
* **Fecha de Entrega:** 20 de mayo de 2026  

---

> ### REGLA DE ORO DE HARDWARE (TIERRAS UNIFICADAS)
> Es obligatorio conectar físicamente el pin **GND** de la ESP32 de la Banda, el pin **GND** de la ESP32-CAM, el pin **GND** del Puente H L298N y el polo negativo (`-`) de la fuente de alimentación externa de 5V. Si no comparten la misma referencia de tierra, el servomotor oscilará erráticamente y las lecturas analógicas del ADC presentarán ruido severo.

---

## Matriz de Asignación de Pines (Capa HAL Libre de Conflictos)

Esta tabla mapea la distribución física y lógica de los pines del microcontrolador hacia los periféricos de entrada y salida del sistema:

| Componente Físico | Sub-Elemento / Pin | Pin ESP32 | Tipo de Pin | Voltaje | Descripción Funcional |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Cerebro y Visión** | **ESP32 S3 CAM** | *Freenove WROVER* | Microcontrolador | 5V (USB/Ext) | Servidor web HTTP síncrono. Captura las imágenes en la ruta `/foto` para el procesamiento del color del brócoli. |
| **Sensor Ultrasónico** | HC-SR04 (VCC) | -- | Alimentación | **5V Obligatorio** | Suministro eléctrico estable para el transductor sónico. |
| | └ Trigger | **Pin 5** | Salida Digital | 3.3V $\rightarrow$ 5V | Envío del pulso sónico para medir altura/diámetro morfológico (Tamaño). |
| | └ Echo | **Pin 18** | Entrada Digital | 5V (Tolerante) | Retorno del eco de distancia hacia la placa central. |
| **Sensor Infrarrojo** | OUT (Presencia) | **Pin 19** | Entrada Digital | 3.3V | Detecta presencia de la hortaliza en la banda para activar el pipeline de IA. (Bajo = Detectado). |
| **Fotorresistencia (LDR)**| Señal Analógica | **Pin 34** | Entrada Analógica | 0V - 3.3V (ADC) | Asegura que la iluminación ambiental sobre la banda sea constante para no afectar las predicciones de la IA. |
| **Servomotor Clasificador**| Cable de Señal | **Pin 13** | Salida PWM (50Hz) | 5V (Potencia Ext)| Mueve los brazos deflectores a 0°, 90° o 180° según la rampa correspondiente. |
| **Driver Puente H L298N** | └ IN1 | **Pin 12** | Salida Digital | 3.3V $\rightarrow$ 5V | Control de dirección A para el arranque/paro del motor de la banda transportadora. |
| | └ IN2 | **Pin 14** | Salida Digital | 3.3V $\rightarrow$ 5V | Control de dirección B para el arranque/paro del motor de la banda transportadora. |
| **Zumbador (Buzzer)** | Terminal Positiva | **Pin 15** | Salida Digital | 3.3V | Alerta acústica si la IA detecta una pieza "echada a perder" (`podrido`). |
| **Diodo LED Verde** | Ánodo (+) | **Pin 2** | Salida Digital | 3.3V (Con Res.) | Indicador visual de Brócoli Óptimo (`apto` / Fresco). |
| **Diodo LED Amarillo**| Ánodo (+) | **Pin 4** | Salida Digital | 3.3V (Con Res.) | Indicador visual de Brócoli de Calidad Media (`floracion`). |
| **Diodo LED Rojo** | Ánodo (+) | **Pin 33** | Salida Digital | 3.3V (Con Res.) | Indicador visual de Brócoli Rechazado (`podrido`). |

---

## 1. Diseño Mecánico de los Recipientes y Rampas Físicas

Según la inferencia calculada en tiempo real por el modelo de IA en el servidor Python, el servomotor despliega un brazo deflector para canalizar físicamente las hortalizas hacia tres contenedores independientes ubicados de manera estratégica a lo largo del chasis:

| Clase (Dataset) | Ángulo Servo | Comportamiento Mecánico | Destino / Contenedor Físico | Estado de Alertas Locales |
| :--- | :--- | :--- | :--- | :--- |
| **`apto` / Fresco** | `0°` | El brazo se mantiene retraído pegado al chasis, dejando el canal libre. | **Recipiente C (Final):** Caja de producto Premium para empaque en fresco y exportación directa. | LED Verde: **ENCENDIDO**<br>Buzzer: Silencio absoluto. |
| **`floracion`** | `90°` | El brazo se despliega a la mitad (90°) bloqueando parcialmente la banda en diagonal. | **Recipiente B (Centro):** Caja de Calidad Media para desvío a congelado o sopas industriales secundarias. | LED Amarillo: **ENCENDIDO**<br>Buzzer: Pitido corto (0.15s). |
| **`podrido`** | `180°` | El brazo se extiende al máximo (180°) barriendo el brócoli hacia el lateral opuesto. | **Recipiente A (Inicio):** Contenedor de Merma y Desecho Orgánico destinado a composta o eliminación. | LED Rojo: **ENCENDIDO**<br>Buzzer: Alerta larga continua (0.60s). |

---

## Arquitectura Física del Flujo de Desvío

El siguiente diagrama de flujo describe el comportamiento dinámico del hardware en la planta desde la detección del objeto hasta su clasificación final:

```text
       ┌────────────────────────────────────────────────────────┐
       │               BANDA TRANSPORTADORA EN MARCHA           │
       └──────────────┬──────────────────┬──────────────────────┘
                      │                  │
                      │ [Objeto Detectado por IR (Pin 19)]
                      ▼
             ┌───────────┐
             │ ESP32-CAM │ ──► Captura e Inferencia de IA (Python)
             └───────────┘                        │
                                                  │
    ┌─────────────────────────────────────────────┴─────────────────────────────────────┐
    │                                             │                                     │
    ▼ (Inferencia: podrido)                       ▼ (Inferencia: floracion)             ▼ (Inferencia: apto)
┌───────────────────────────┐               ┌───────────────────────────┐         ┌───────────────────────────┐
│       RECIPIENTE A        │               │       RECIPIENTE B        │         │       RECIPIENTE C        │
│  [Servo se mueve a 180°]  │               │   [Servo se mueve a 90°]  │         │ [Servo se mantiene a 0°]  │
│   Rampa Lateral Izquierda │               │       Rampa Central       │         │   Flujo Continuo Lineal   │
│ Descarte / Merma Orgánica │               │ Procesamiento Industrial  │         │ Embarque / Venta Fresca   │
└───────────────────────────┘               └───────────────────────────┘         └───────────────────────────┘
              ▲                                           ▲                                     ▲
        Buzzer Largo                                Buzzer Corto                             Silencio
          LED Rojo                                  LED Amarillo                             LED Verde
