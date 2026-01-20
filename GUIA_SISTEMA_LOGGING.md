# 📊 Sistema de Logging - Guía Completa

## 🎯 ¿Qué es el Sistema de Logging?

El bot ahora incluye un **sistema completo de logging** que registra TODO lo que hace en archivos `.log` con timestamps, permitiéndote:

✅ **Ver exactamente qué está detectando** el bot  
✅ **Debuggear problemas** sin tener que estar mirando la consola  
✅ **Enviar logs al desarrollador** para análisis  
✅ **Revisar sesiones pasadas** para optimizar configuración  
✅ **Entender por qué fallan** las detecciones de supply drops, dinos, etc.

---

## 📁 Ubicación de los Logs

Cuando ejecutes el bot, se crean automáticamente:

```
jwa_bot/
├── logs/
│   ├── bot_log_20260119_143000.log  ← Sesión del 19/01 a las 14:30
│   ├── bot_log_20260119_150000.log  ← Sesión del 19/01 a las 15:00
│   └── bot_log_20260119_173045.log  ← Sesión más reciente
├── debug_screenshots/
│   └── (imágenes capturadas si activas debug visual)
├── jw_bot.py
└── main.py
```

**Cada vez que ejecutas el bot, se crea un NUEVO archivo de log** con la fecha y hora exactas.

---

## 📝 Formato de los Logs

Cada línea del log tiene este formato:

```
[FECHA HORA] [NIVEL] MENSAJE
```

**Ejemplo:**
```
[2026-01-19 14:30:15] [INFO] 🦖 JURASSIC WORLD ALIVE BOT - INICIADO
[2026-01-19 14:30:16] [DEBUG] 🔍 Buscando supply drops...
[2026-01-19 14:30:17] [INFO] 🟠 [SUPPLY DROP] Detectados 3 supply drops
[2026-01-19 14:30:18] [WARNING] ❌ [ESTADO DETECTADO] NO IDENTIFICADO
```

---

## 🎨 Niveles de Logging

### 🟢 [INFO] - Información General
**¿Qué muestra?**
- Inicio y fin del bot
- Configuración de ventana BlueStacks
- Supply drops / dinos / monedas detectados
- Estados reconocidos por OCR
- Cambios de ubicación

**Ejemplo:**
```
[INFO] 🦖 JURASSIC WORLD ALIVE BOT - INICIADO
[INFO] 📍 Posición X: 110px
[INFO] 📏 Ancho (W): 1400px
[INFO] 🟠 [SUPPLY DROP] Detectados 3 supply drops
[INFO] ✅ [ESTADO DETECTADO] SUPPLY
```

**¿Cuándo verlo?**
- Siempre visible en consola
- Registrado en archivo .log
- Ver este nivel para operación normal

---

### 🔵 [DEBUG] - Información Detallada

**¿Qué muestra?**
- Rangos de colores RGB usados
- Tamaño de zonas de captura
- Píxeles detectados en análisis de color
- Número de componentes encontrados
- Tamaño y posición de cada objeto
- Áreas de OCR capturadas
- Palabras clave detectadas

**Ejemplo:**
```
[DEBUG] 🔍 Buscando supply drops...
[DEBUG]    📊 Supply color range: R[160-255] G[60-255] B[0-120]
[DEBUG]    📐 Zona analizada: (328, 560, 3)
[DEBUG]    🎨 Píxeles detectados inicialmente: 1234
[DEBUG]    🔢 Componentes detectados: 3
[DEBUG]    ✅ Supply drop #1: 156 píxeles en posición (300, 250)
[DEBUG]    📐 Área botón lanzar: (62, 178, 3)
[DEBUG]    📦 Palabras clave de SUPPLY detectadas
```

**¿Cuándo verlo?**
- Solo en archivo .log (no en consola por defecto)
- Para debugging avanzado
- Para enviar al desarrollador

**¿Cómo activarlo en consola?**
En `jw_bot.py` línea ~47, cambia:
```python
# De:
logger = setup_logging(log_level=logging.INFO)

# A:
logger = setup_logging(log_level=logging.DEBUG)
```

---

### 🟡 [WARNING] - Advertencias

**¿Qué muestra?**
- OCR no pudo identificar el estado
- Detección incierta
- Posibles falsos positivos

**Ejemplo:**
```
[WARNING] ❌ [ESTADO DETECTADO] NO IDENTIFICADO - OCR puede haber fallado
[WARNING]    💡 Considera activar debug visual para ver qué captura el OCR
```

**¿Cuándo aparece?**
- Cuando el OCR no encuentra palabras clave conocidas
- Cuando algo no sale como esperado pero el bot puede continuar

---

### 🔴 [ERROR] - Errores Críticos

**¿Qué muestra?**
- Errores que impiden continuar
- Fallos en captura de pantalla
- Problemas de configuración

**Ejemplo:**
```
[ERROR] No se pudo capturar pantalla en región (110, 110, 1400, 700)
[ERROR] Tesseract no está instalado o no se encuentra en el PATH
```

**¿Qué hacer?**
- El bot puede detenerse
- Revisar el error específico
- Corregir la configuración

---

## 📖 Cómo Leer un Log Completo

### Ejemplo de Log de Inicio:

```
[2026-01-19 14:30:00] [INFO] ================================================================================
[2026-01-19 14:30:00] [INFO] 🦖 JURASSIC WORLD ALIVE BOT - INICIADO
[2026-01-19 14:30:00] [INFO] ================================================================================
[2026-01-19 14:30:00] [INFO] 📁 Log guardado en: logs/bot_log_20260119_143000.log
[2026-01-19 14:30:00] [INFO] 🔧 Inicializando Bot...
[2026-01-19 14:30:00] [INFO] 📁 Carpeta 'debug_screenshots' creada
[2026-01-19 14:30:01] [INFO] ================================================================================
[2026-01-19 14:30:01] [INFO] 🎮 INSTRUCCIONES DE CALIBRACIÓN
[2026-01-19 14:30:01] [INFO] ================================================================================
[2026-01-19 14:30:01] [INFO] 1️⃣  Abre BlueStacks con Jurassic World Alive en el MAPA
[2026-01-19 14:30:01] [INFO] 2️⃣  Presiona 'a' y haz click en ESQUINA SUPERIOR IZQUIERDA del juego
[2026-01-19 14:30:01] [INFO] 3️⃣  Presiona 'a' otra vez y haz click en ESQUINA INFERIOR DERECHA
[2026-01-19 14:30:01] [INFO] 4️⃣  El bot empezará a funcionar automáticamente
[2026-01-19 14:30:01] [INFO] ❌ Presiona 'q' para detener el bot en cualquier momento
[2026-01-19 14:30:01] [INFO] ================================================================================
```

**¿Qué te dice?**
- ✅ Bot iniciado correctamente
- ✅ Log file creado
- ✅ Carpetas preparadas
- ✅ Instrucciones mostradas

---

### Ejemplo de Log de Calibración:

```
[2026-01-19 14:30:15] [INFO] 🔘 Tecla 'a' presionada
[2026-01-19 14:30:15] [INFO] ✅ Primer punto capturado: (110, 110)
[2026-01-19 14:30:15] [INFO] 👉 Ahora presiona 'a' de nuevo y haz click en la esquina inferior derecha
[2026-01-19 14:30:20] [INFO] 🔘 Tecla 'a' presionada
[2026-01-19 14:30:20] [INFO] ✅ Segundo punto capturado: (1510, 810)
[2026-01-19 14:30:20] [INFO] ================================================================================
[2026-01-19 14:30:20] [INFO] 📐 CONFIGURACIÓN DE VENTANA BLUESTACKS
[2026-01-19 14:30:20] [INFO] ================================================================================
[2026-01-19 14:30:20] [INFO] 📍 Posición X: 110px
[2026-01-19 14:30:20] [INFO] 📍 Posición Y: 110px
[2026-01-19 14:30:20] [INFO] 📏 Ancho (W): 1400px
[2026-01-19 14:30:20] [INFO] 📏 Alto (H): 700px
[2026-01-19 14:30:20] [INFO] 🎯 Esquina superior izquierda: (110, 110)
[2026-01-19 14:30:20] [INFO] 🎯 Esquina inferior derecha: (1510, 810)
[2026-01-19 14:30:20] [INFO] ================================================================================
[2026-01-19 14:30:20] [INFO] 🎯 Shooting zone: Y[161-489] X[14-574]
[2026-01-19 14:30:20] [INFO] 🚀 Launch button: Y[549-601] X[185-435]
[2026-01-19 14:30:20] [INFO] 📝 Supply text area: Y[126-210] X[112-560]
[2026-01-19 14:30:20] [INFO] 🚀 Calibración completa! El bot comenzará a operar...
```

**¿Qué te dice?**
- ✅ Calibración exitosa
- ✅ Coordenadas capturadas correctamente
- ✅ Zonas calculadas
- ✅ Bot listo para operar

**¿Qué verificar?**
- `Ancho (W)` y `Alto (H)` deben ser similares a tu resolución de BlueStacks
- `Shooting zone` debe cubrir ~60-70% del alto y ~40-45% del ancho

---

### Ejemplo de Log de Detección de Supply Drops:

```
[2026-01-19 14:30:25] [DEBUG] 🔍 Buscando supply drops...
[2026-01-19 14:30:25] [DEBUG]    📊 Supply color range: R[160-255] G[60-255] B[0-120]
[2026-01-19 14:30:25] [DEBUG]    📊 Event color range: R[0-180] G[120-255] B[0-180]
[2026-01-19 14:30:25] [DEBUG]    📐 Zona analizada: (328, 560, 3)
[2026-01-19 14:30:25] [DEBUG]    🎨 Píxeles detectados inicialmente: 1234
[2026-01-19 14:30:25] [DEBUG]    🔢 Componentes detectados: 3
[2026-01-19 14:30:25] [DEBUG]    ✅ Supply drop #1: 156 píxeles en posición (300, 250)
[2026-01-19 14:30:25] [DEBUG]    ✅ Supply drop #2: 203 píxeles en posición (400, 350)
[2026-01-19 14:30:25] [DEBUG]    ✅ Supply drop #3: 187 píxeles en posición (250, 450)
[2026-01-19 14:30:25] [INFO] 🟠 [SUPPLY DROP] Detectados 3 supply drops: [[300, 250], [400, 350], [250, 450]]
```

**¿Qué te dice?**
- ✅ Supply drops detectados correctamente
- ✅ Colores RGB configurados
- ✅ 3 supply drops encontrados con sus posiciones

**¿Qué significa cada número?**
- `Píxeles detectados inicialmente: 1234` → Cantidad de píxeles que coinciden con el rango de color
- `Componentes detectados: 3` → Objetos separados encontrados
- `156 píxeles en posición (300, 250)` → Tamaño del supply drop y su posición

**Si ves `Píxeles detectados inicialmente: 0`:**
- ❌ No se detectaron colores coincidentes
- 🔧 Necesitas calibrar los rangos RGB

---

### Ejemplo de Log de OCR:

```
[2026-01-19 14:30:30] [DEBUG] 🔍 Determinando estado del objeto...
[2026-01-19 14:30:30] [DEBUG]    📐 Área botón lanzar: (62, 178, 3)
[2026-01-19 14:30:30] [DEBUG]    📐 Área texto supply: (100, 320, 3)
[2026-01-19 14:30:30] [INFO] 📝 [OCR] Botón: 'LANZAR'
[2026-01-19 14:30:30] [INFO] 📝 [OCR] Texto: 'SUMINISTRO'
[2026-01-19 14:30:30] [INFO] 📝 [OCR] Combinado: 'LANZAR SUMINISTRO'
[2026-01-19 14:30:30] [DEBUG]    📦 Palabras clave de SUPPLY detectadas
[2026-01-19 14:30:30] [INFO] ✅ [ESTADO DETECTADO] SUPPLY
```

**¿Qué te dice?**
- ✅ OCR funcionando correctamente
- ✅ Detectó "LANZAR" en el botón
- ✅ Detectó "SUMINISTRO" en el área de texto
- ✅ Estado identificado como SUPPLY

**Si ves OCR vacío:**
```
[INFO] 📝 [OCR] Botón: ''
[INFO] 📝 [OCR] Texto: ''
[WARNING] ❌ [ESTADO DETECTADO] NO IDENTIFICADO
```
- ❌ OCR no pudo leer nada
- 🔧 Problema: área de captura incorrecta O Tesseract no instalado

---

### Ejemplo de Log de Finalización:

```
[2026-01-19 15:00:00] [INFO] ================================================================================
[2026-01-19 15:00:00] [INFO] ⛔ BOT DETENIDO POR USUARIO
[2026-01-19 15:00:00] [INFO] ================================================================================
[2026-01-19 15:00:00] [INFO] 📊 RESUMEN DE RECURSOS COLECTADOS:
[2026-01-19 15:00:00] [INFO] --------------------------------------------------------------------------------
[2026-01-19 15:00:00] [INFO] 📦 SUMINISTROS:
[2026-01-19 15:00:00] [INFO]    • Cash: 1500
[2026-01-19 15:00:00] [INFO]    • Coins: 5000
[2026-01-19 15:00:00] [INFO]    • Darts: 250
[2026-01-19 15:00:00] [INFO] 🦖 DINOSAURIOS:
[2026-01-19 15:00:00] [INFO]    • Triceratops: 120
[2026-01-19 15:00:00] [INFO]    • Velociraptor: 85
[2026-01-19 15:00:00] [INFO] ================================================================================
[2026-01-19 15:00:00] [INFO] ✅ Sesión finalizada. Log guardado en carpeta 'logs/'
[2026-01-19 15:00:00] [INFO] ================================================================================
```

**¿Qué te dice?**
- ✅ Sesión terminada normalmente
- ✅ Recursos colectados resumidos
- ✅ Log guardado

---

## 🔍 Cómo Analizar Problemas con los Logs

### Problema: "No detecta supply drops"

**1. Busca en el log:**
```
[DEBUG] 🔍 Buscando supply drops...
```

**2. Verifica los píxeles detectados:**
```
[DEBUG]    🎨 Píxeles detectados inicialmente: 0
```

**Si es 0:**
- ❌ Los colores RGB no coinciden
- 🔧 Solución: Calibrar colores (ver `GUIA_COLORES_Y_CALIBRACION.md`)

**Si es >0 pero no muestra componentes:**
```
[DEBUG]    🔢 Componentes detectados: 0
```
- ❌ Los píxeles están muy dispersos
- 🔧 Solución: Ajustar rangos RGB o reducir umbral de píxeles

**Si muestra componentes pero son muy pequeños:**
```
[DEBUG]    ✅ Supply drop #1: 5 píxeles en posición (300, 250)
```
- ❌ Componente menor a 10 píxeles, se descarta
- 🔧 Solución: Ajustar rangos RGB para detectar más píxeles

---

### Problema: "OCR no reconoce texto"

**1. Busca en el log:**
```
[INFO] 📝 [OCR] Botón: ''
[INFO] 📝 [OCR] Texto: ''
```

**Si ambos están vacíos:**
- ❌ Tesseract no está funcionando O área de captura incorrecta

**2. Verifica el tamaño del área:**
```
[DEBUG]    📐 Área botón lanzar: (62, 178, 3)
[DEBUG]    📐 Área texto supply: (100, 320, 3)
```

**Si algún valor es muy pequeño (<50 píxeles):**
- ❌ El área no captura suficiente texto
- 🔧 Solución: Ajustar `supply_drop_text_loc_ratio` en `jw_bot.py`

**Si los tamaños son correctos pero OCR está vacío:**
- ❌ Tesseract no instalado o mal configurado
- 🔧 Solución: Instalar Tesseract y descomentar configuración en línea ~20

---

### Problema: "Detecta pero no recolecta"

**1. Busca:**
```
[INFO] 🟠 [SUPPLY DROP] Detectados 3 supply drops
```
✅ Detección OK

**2. Luego busca:**
```
[INFO] 📝 [OCR] Texto: 'ALGO_RARO'
[WARNING] ❌ [ESTADO DETECTADO] NO IDENTIFICADO
```

**Si el estado no se identifica:**
- ❌ El texto OCR no contiene palabras clave conocidas
- 🔧 Solución: Activar debug visual para ver qué texto captura

---

## 📤 Cómo Enviar Logs al Desarrollador

### Paso 1: Encuentra el Log Más Reciente

```bash
# Windows PowerShell
cd "C:\ruta\a\jwa_bot"
dir logs

# Mac/Linux Terminal
cd /ruta/a/jwa_bot
ls -ltr logs/
```

El archivo más reciente será el último en la lista.

### Paso 2: Abre el Archivo

```bash
# Windows Notepad
notepad logs\bot_log_20260119_143000.log

# Mac
open logs/bot_log_20260119_143000.log

# Linux
gedit logs/bot_log_20260119_143000.log
```

### Paso 3: Copia el Contenido

- Selecciona todo (Ctrl+A / Cmd+A)
- Copia (Ctrl+C / Cmd+C)

### Paso 4: Envía al Desarrollador

**Opción A: Crear un Issue en GitHub**
1. Ve a: https://github.com/MigueAmaterasu/jwa_bot/issues
2. Click "New Issue"
3. Título: "Problema: [describe el problema]"
4. Descripción:
   ```
   **Problema:**
   [Describe qué está fallando]
   
   **Configuración:**
   - SO: Windows 10 / macOS / Linux
   - Resolución BlueStacks: 1600x900
   - Versión Python: 3.x
   
   **Log completo:**
   ```
   [Pega aquí todo el contenido del log]
   ```
   ```

**Opción B: Adjuntar Archivo**
- Simplemente adjunta el archivo .log al issue/correo

### Información Adicional Útil

Junto con el log, incluye:
- 📸 Captura de pantalla de BlueStacks con el juego visible
- 🖼️ Si activaste debug visual, la carpeta `debug_screenshots/`
- 💻 Tu configuración de BlueStacks (resolución, DPI)
- 🎨 Si modificaste colores RGB, indica cuáles

---

## ⚙️ Configuración Avanzada del Logging

### Cambiar Nivel de Detalle en Consola

En `jw_bot.py` línea ~47:

```python
# Opción 1: Solo INFO y superiores (menos ruido)
logger = setup_logging(log_level=logging.INFO)

# Opción 2: Todo incluyendo DEBUG (más detalle)
logger = setup_logging(log_level=logging.DEBUG)

# Opción 3: Solo WARNING y errores (mínimo)
logger = setup_logging(log_level=logging.WARNING)
```

**Nota:** El archivo .log SIEMPRE tiene nivel DEBUG completo.

### Desactivar Logging en Archivo

Si solo quieres ver en consola (no recomendado):

En `jw_bot.py` línea ~32-36, comenta:

```python
# file_handler = logging.FileHandler(log_filename, encoding='utf-8')
# file_handler.setFormatter(log_format)
# file_handler.setLevel(logging.DEBUG)
# logger.addHandler(file_handler)
```

---

## 📊 Resumen de Emojis Usados

| Emoji | Significado |
|-------|-------------|
| 🦖 | Bot/Dinosaurio |
| 🎮 | Instrucciones/Calibración |
| 📍 | Posición/Coordenadas |
| 📏 | Dimensiones |
| 🎯 | Zonas de detección |
| 🟠 | Supply drop |
| 🪙 | Monedas |
| 📝 | OCR/Texto |
| 🔍 | Búsqueda/Detección |
| ✅ | Éxito |
| ❌ | Fallo/Error |
| 🔧 | Configuración |
| 📊 | Datos/Estadísticas |
| 💡 | Sugerencia |
| ⛔ | Detenido |
| 🚀 | Lanzar/Comenzar |

---

**Última actualización:** 19 de enero de 2026  
**Versión:** 3.0 (Sistema de Logging Completo)
