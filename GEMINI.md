# REGLAS Y CONTEXTO DEL WORKSPACE (GEMINI.md)

Este archivo es leído automáticamente por el asistente de IA en cada sesión de trabajo dentro de este repositorio.

---

## 1. Contexto del Proyecto
* **Proyecto:** Sistema Embebido para Captura y Análisis de Señales Cardiorrespiratorias.
* **Curso / Nivel:** 8vo Semestre (2026) — Asignatura: *f tecno*.
* **Enfoque Actual:** **Consolidar una base robusta de captura y acondicionamiento de datos biomédicos** (ópticos y acústicos).
* **Visión a Futuro:** Arquitectura modular desacoplada que permita derivar diferentes implementaciones (triaje embebido con semáforo LED, estetoscopio inteligente con TinyML, telemetría IoT o datalogger médico).

---

## 2. Hardware Físico en Posesión del Equipo
* **Microcontrolador:** ESP32 (3.3V, Dual Core, soporte I2C e I2S por hardware).
* **Canal Óptico:** Sensor MAX30102 (Pulsioximetría $SpO_2$ y fotopletismografía PPG por bus I2C).
* **Canal Acústico:** Micrófono MEMS digital INMP441 (Audio digital de auscultación/tos por bus I2S).
* **Feedback Visual:** Módulo Neopixel WS2812 de 8 LEDs (Línea de datos GPIO 4).
* **Alimentación Autónoma:** Celda de litio (3.7V) + Módulo de carga/protección TP4056 + Switch Rocker mecánico On/Off.

---

## 3. Directrices Obligatorias para la IA en Cada Chat
1. **Priorizar la base de captura:** Antes de avanzar hacia modelos complejos de IA o conectividad en la nube, asegurar que la adquisición de datos crudos (I2C para MAX30102 e I2S para INMP441) sea limpia, estable y repetible.
2. **Modularidad en el código:** Diseñar el firmware de manera que la capa de captura de datos esté separada de la capa de procesamiento/visualización, permitiendo cambiar de implementación fácilmente.
3. **Manejo del micrófono INMP441:** El sensor es estrictamente digital I2S. No usar lecturas analógicas (`analogRead`). Usar librerías I2S nativas de ESP32.
4. **Alimentación y seguridad:** El interruptor On/Off debe cortar la línea `OUT+` hacia el pin `VIN` del ESP32. Mantener la alimentación lógica de sensores en `3V3`.
5. **Documentación de referencia:**
   * Contexto maestro: [INSTRUCCIONES_PROYECTO.md](file:///Users/wilsonjonatan/Documents/8vo%202026/f%20tecno/code/INSTRUCCIONES_PROYECTO.md)
   * Guía de Datos e IA: [INSTRUCCIONES_DATOS_IA.md](file:///Users/wilsonjonatan/Documents/8vo%202026/f%20tecno/code/INSTRUCCIONES_DATOS_IA.md)
   * Inventario de datos clínicos: [docs/RESUMEN_DATOS.md](file:///Users/wilsonjonatan/Documents/8vo%202026/f%20tecno/code/docs/RESUMEN_DATOS.md)
   * Bitácora de avances: [docs/AVANCES_PROYECTO.md](file:///Users/wilsonjonatan/Documents/8vo%202026/f%20tecno/code/docs/AVANCES_PROYECTO.md)
   * Hoja de ruta y pendientes: [docs/TAREAS_PENDIENTES.md](file:///Users/wilsonjonatan/Documents/8vo%202026/f%20tecno/code/docs/TAREAS_PENDIENTES.md)
