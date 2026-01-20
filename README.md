# 🦖 Jurassic World Alive Bot

Bot automatizado para recolectar recursos en Jurassic World Alive usando BlueStacks.

## 🎯 Características

✅ **Recolección automática** de supply drops, eventos especiales y monedas  
✅ **Captura de dinosaurios** con sistema de puntería inteligente  
✅ **Sistema de logging completo** para debugging y análisis  
✅ **Calibración visual** paso a paso  
✅ **Detección por color RGB** configurable  
✅ **OCR multiidioma** (español/inglés)  
✅ **Cambio automático de ubicación** cuando se agotan recursos  

---

## 📋 Requisitos

### Software
- **Python 3.7+**
- **BlueStacks** (emulador de Android)
- **Tesseract OCR** ([Descargar aquí](https://github.com/tesseract-ocr/tesseract))
- **Jurassic World Alive** instalado en BlueStacks

### Dependencias Python
```bash
pip install -r requirements.txt
```

Contenido de `requirements.txt`:
```
matplotlib
numpy
scikit-image
PyAutoGUI
pytesseract
keyboard
Pillow==9.5.0
```

---

## 🚀 Instalación Rápida

### 1. Clonar el Repositorio
```bash
git clone https://github.com/MigueAmaterasu/jwa_bot.git
cd jwa_bot
```

### 2. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 3. Instalar Tesseract OCR

#### Windows:
1. Descargar desde: https://github.com/tesseract-ocr/tesseract
2. Instalar en `C:\Program Files\Tesseract-OCR\`
3. En `jw_bot.py` línea ~20, descomenta:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
   ```

#### macOS:
```bash
brew install tesseract
```

#### Linux:
```bash
sudo apt-get install tesseract-ocr
```

### 4. Configurar BlueStacks

**Resolución recomendada:**
- 1600x900 (16:9) o 1280x720 (16:9)
- DPI: 240 (Medium)
- Modo ventana (no pantalla completa)

---

## 🎮 Uso

### 1. Abrir BlueStacks
- Inicia BlueStacks
- Abre Jurassic World Alive
- Ve al **mapa principal**

### 2. Ejecutar el Bot
```bash
python main.py
```

### 3. Calibrar Ventana

Verás instrucciones en consola:

```
[INFO] 1️⃣  Abre BlueStacks con Jurassic World Alive en el MAPA
[INFO] 2️⃣  Presiona 'a' y haz click en ESQUINA SUPERIOR IZQUIERDA del juego
[INFO] 3️⃣  Presiona 'a' otra vez y haz click en ESQUINA INFERIOR DERECHA
[INFO] 4️⃣  El bot empezará a funcionar automáticamente
```

**Diagrama de calibración:**
```
┌─────────────────────────────────────────┐
│ BlueStacks            [─][□][✕]        │
├─────────────────────────────────────────┤
│ ✕ PRIMER CLICK (esquina sup. izq.)     │
│                                         │
│        JURASSIC WORLD ALIVE             │
│                                         │
│                 ✕ SEGUNDO CLICK         │
│                   (esquina inf. der.)   │
└─────────────────────────────────────────┘
```

### 4. Detener el Bot

Presiona **'q'** en cualquier momento para detener el bot de forma segura.

---

## 📊 Sistema de Logging

El bot registra TODA su actividad en archivos de log con timestamps:

```
jwa_bot/
├── logs/
│   ├── bot_log_20260119_143000.log
│   └── bot_log_20260119_150000.log
└── debug_screenshots/
    └── (capturas de debug si se activan)
```

### Niveles de Log

| Nivel | Descripción |
|-------|-------------|
| 🟢 INFO | Operación normal |
| 🔵 DEBUG | Detalles técnicos |
| 🟡 WARNING | Advertencias |
| 🔴 ERROR | Errores críticos |

### Ver Logs
```bash
# Windows
notepad logs\bot_log_*.log

# Mac/Linux
cat logs/bot_log_*.log
```

---

## 🎨 Configuración de Colores

Los colores RGB para detección se configuran en `jw_bot.py` líneas ~70-160.

### Colores por Defecto

**Supply Drops (naranja/amarillo):**
```python
self.supply_drop_color = (160, 60, 0, 255, 255, 120)
```

**Eventos Especiales (verde):**
```python
self.special_event_color = (0, 120, 0, 180, 255, 180)
```

**Monedas (dorado):**
```python
self.coin_color = (180, 160, 100, 240, 220, 120)
```

### Calibrar Colores

1. Toma una captura de pantalla con supply drop visible
2. Usa un **color picker** para obtener valores RGB
3. Actualiza los rangos en `jw_bot.py`

Ver: [`GUIA_COLORES_Y_CALIBRACION.md`](GUIA_COLORES_Y_CALIBRACION.md)

---

## 📖 Documentación Completa

| Guía | Descripción |
|------|-------------|
| **[GUIA_CALIBRACION_BLUESTACKS.md](GUIA_CALIBRACION_BLUESTACKS.md)** | Cómo calibrar la ventana correctamente |
| **[GUIA_SISTEMA_LOGGING.md](GUIA_SISTEMA_LOGGING.md)** | Cómo interpretar y usar los logs |
| **[GUIA_COLORES_Y_CALIBRACION.md](GUIA_COLORES_Y_CALIBRACION.md)** | Cómo ajustar colores RGB |
| **[CAMBIOS_REALIZADOS.md](CAMBIOS_REALIZADOS.md)** | Historial de correcciones (v1-2) |
| **[RESUMEN_COLORES_OCR.md](RESUMEN_COLORES_OCR.md)** | Correcciones de OCR y colores |
| **[RESUMEN_LOGGING_IMPLEMENTADO.md](RESUMEN_LOGGING_IMPLEMENTADO.md)** | Sistema de logging (v3) |

---

## 🐛 Troubleshooting

### Problema: No detecta supply drops

**Síntomas:**
```
[DEBUG] 🎨 Píxeles detectados inicialmente: 0
```

**Soluciones:**
1. Calibrar colores RGB (ver guía)
2. Reducir umbral de píxeles en línea ~333
3. Verificar zona de búsqueda en logs

---

### Problema: OCR no reconoce texto

**Síntomas:**
```
[INFO] 📝 [OCR] Botón: ''
[INFO] 📝 [OCR] Texto: ''
```

**Soluciones:**
1. Verificar que Tesseract esté instalado
2. Activar debug visual (descomentar línea ~1034)
3. Ajustar área de captura si es muy pequeña

---

### Problema: Calibración incorrecta

**Síntomas:**
```
[INFO] 📏 Ancho (W): 50px
```

**Solución:**
- Recalibrar presionando 'a' dos veces correctamente
- Primera 'a' → Click esquina superior izquierda
- Segunda 'a' → Click esquina inferior derecha

---

## 🔧 Debug Avanzado

### Activar Debug Visual

En `jw_bot.py` línea ~1034, descomenta:
```python
self.debug_save_ocr_regions(background_new, f"supply_{pos[0]}_{pos[1]}")
```

Las imágenes se guardarán en `debug_screenshots/` mostrando exactamente qué captura el bot.

### Cambiar Nivel de Logging

En `jw_bot.py` línea ~47:
```python
# Para ver TODO en consola (incluido DEBUG)
logger = setup_logging(log_level=logging.DEBUG)

# Para ver solo lo esencial (INFO y superiores)
logger = setup_logging(log_level=logging.INFO)
```

---

## 📊 Estadísticas del Bot

Al detener el bot con 'q', verás un resumen:

```
[INFO] 📊 RESUMEN DE RECURSOS COLECTADOS:
[INFO] 📦 SUMINISTROS:
[INFO]    • Cash: 1500
[INFO]    • Coins: 5000
[INFO]    • Darts: 250
[INFO] 🦖 DINOSAURIOS:
[INFO]    • Triceratops: 120
[INFO]    • Velociraptor: 85
```

---

## 🤝 Contribuir

### Reportar Bugs

1. Ve a [Issues](https://github.com/MigueAmaterasu/jwa_bot/issues)
2. Click "New Issue"
3. Incluye:
   - Archivo de log completo
   - Captura de pantalla
   - Descripción del problema
   - Tu configuración (SO, resolución BlueStacks, etc.)

### Enviar Pull Requests

1. Fork el repositorio
2. Crea una rama: `git checkout -b feature/mi-mejora`
3. Commit cambios: `git commit -am 'Agrega nueva funcionalidad'`
4. Push: `git push origin feature/mi-mejora`
5. Crea un Pull Request

---

## ⚖️ Disclaimer

Este bot es solo para **propósitos educativos**. 

⚠️ **IMPORTANTE:**
- Usar bots puede violar los Términos de Servicio del juego
- Usar bajo tu propio riesgo
- El autor no se hace responsable de baneos o penalizaciones

---

## 📜 Licencia

Este proyecto está bajo la licencia MIT. Ver archivo `LICENSE` para más detalles.

---

## 📧 Contacto

- **GitHub:** [@MigueAmaterasu](https://github.com/MigueAmaterasu)
- **Repo:** [jwa_bot](https://github.com/MigueAmaterasu/jwa_bot)

---

## 🙏 Agradecimientos

- Jurassic World Alive por el juego
- Comunidad de Python por las librerías
- Tesseract OCR por el motor de reconocimiento de texto

---

## 📅 Changelog

### v3.0 (19 Enero 2026)
✅ Sistema completo de logging implementado  
✅ Logs con timestamps y niveles  
✅ Documentación completa de calibración  
✅ Debug visual mejorado  

### v2.0 (19 Enero 2026)
✅ Área de OCR corregida  
✅ Detección de estado mejorada  
✅ Colores RGB documentados  
✅ Sistema de debug visual  

### v1.0 (19 Enero 2026)
✅ Bug de batería invertida corregido  
✅ Timeout aumentado de 60s a 120s  
✅ Umbral de píxeles reducido  
✅ Detección de supply drops mejorada  

---

**Versión Actual:** 3.0  
**Estado:** ✅ Producción - Listo para usar  
**Última Actualización:** 19 de enero de 2026

---

## 🚀 Quick Start

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Instalar Tesseract OCR
# (ver sección de instalación)

# 3. Abrir BlueStacks con JWA en el mapa

# 4. Ejecutar bot
python main.py

# 5. Calibrar con 'a' + 'a'

# 6. ¡Disfrutar!
```

**¿Problemas?** → Revisa [`GUIA_SISTEMA_LOGGING.md`](GUIA_SISTEMA_LOGGING.md) y envía tus logs!

---

Made with 🦖 by MigueAmaterasu
