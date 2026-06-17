# BroccoSort AI: Sistema Automatizado de Clasificación de Hortalizas por Visión y Morfología

## Objetivo del Proyecto
Implementar un sistema automatizado de clasificación de hortalizas que utiliza visión artificial y sensores físicos para categorizar brócoli según su estado de madurez (color) y dimensiones (tamaño). El sistema busca optimizar la producción agrícola local mediante una banda transportadora controlada por un ESP32 S3 CAM, la cual desvía automáticamente el producto de baja calidad, emite alertas sonoras y visuales, y permite el monitoreo remoto de estadísticas de producción a través de una interfaz web y notificaciones en la nube.

---

## Integrantes
* **Mayra Paola Martínez Aranda** (Clave: 22240233)
* **Nissi Sarahi Prats Ramírez** (Clave: 23240003)
* **Erik Fabian Gonsalez Jimenez** (Clave: 23240022)

**Materia:** Sistemas Programables 
**Institución:** Instituto Tecnológico de León (TecNM Campus León)

---

## Estructura del Sistema Unificado
```text
├── 📂 Documentación
│   ├── 📄 Analisis_Individual.md
│   └── 📄 Matriz_Topicos.md
├── 📂 ESP32_Banda
│   ├── 📄 comunicacion_mqtt.py
│   ├── 📄 dispositivos.py
│   └── 📄 main.py
├── 📂 ESP32_Cámara
│   └── 📄 main.py
├── 📂 Interfaz
│   ├── 📄 index.html
│   └── 📄 Link De Pagina Web.txt
├── 📂 Servidor_Python
│   ├── 📄 DATASET_2.py
│   └── 📄 servidor_broccosort.py
└── 📄 LÉAME.md
