# 🎯 Guía de Calibración BlueStacks - Jurassic World Alive Bot

## 📋 Índice
1. [Preparación de BlueStacks](#preparación-de-bluestacks)
2. [Dónde Hacer Click para Calibrar](#dónde-hacer-click-para-calibrar)
3. [Proceso de Calibración Paso a Paso](#proceso-de-calibración-paso-a-paso)
4. [Verificación de Coordenadas](#verificación-de-coordenadas)
5. [Interpretación de Logs](#interpretación-de-logs)
6. [Troubleshooting](#troubleshooting)

---

## 🖥️ Preparación de BlueStacks

### Paso 1: Configuración Recomendada de BlueStacks

#### Resolución Recomendada:
```
📱 Resolución: 1600x900 (16:9)
   o
📱 Resolución: 1280x720 (16:9)
```

**¿Cómo cambiar resolución en BlueStacks?**
1. Cierra BlueStacks completamente
2. Abre **BlueStacks Settings** (desde el icono en la bandeja del sistema)
3. Ve a **Display**
4. Configura:
   - **Display Resolution:** 1600x900 o 1280x720
   - **DPI:** 240 (Medium)
5. Guarda y reinicia BlueStacks

#### Configuración de Ventana:
```
✅ Modo Ventana (no pantalla completa)
✅ Sin bordes decorativos (si es posible)
✅ Tamaño fijo (no cambiar durante uso del bot)
```

### Paso 2: Posicionar la Ventana

**IMPORTANTE:** La ventana de BlueStacks debe estar:
- ✅ Completamente visible en pantalla
- ✅ Sin partes cortadas/ocultas
- ✅ En la misma posición siempre que uses el bot

**Posición Recomendada:**
```
┌─────────────────────────────────────────────────┐
│         TU PANTALLA PRINCIPAL                   │
│                                                 │
│  ┌────────────────────────────┐                │
│  │                            │                │
│  │     BLUESTACKS             │                │
│  │                            │                │
│  │  (Centrado o esquina       │                │
│  │   superior izquierda)      │                │
│  │                            │                │
│  └────────────────────────────┘                │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 🎯 Dónde Hacer Click para Calibrar

### Visualización de la Ventana BlueStacks

Cuando ejecutes el bot y presiones la tecla **'a'** dos veces, debes clickear en estas posiciones exactas:

```
VENTANA BLUESTACKS CON JURASSIC WORLD ALIVE
┌─────────────────────────────────────────────────────────┐
│ ⚙️ [BlueStacks Controls]                     ─  □  ✕  │ ← BARRA DE TÍTULO (NO CLICKEAR AQUÍ)
├─────────────────────────────────────────────────────────┤
│                                                         │
│   PRIMER CLICK AQUÍ →  ✕ (Esquina superior izquierda) │
│   🎯 Justo después de la barra de título              │
│   📍 Dentro del área del juego                         │
│                                                         │
│                                                         │
│                                                         │
│              JUEGO JURASSIC WORLD ALIVE                │
│                    (Mapa visible)                       │
│                                                         │
│                                                         │
│                                                         │
│                                                         │
│                                                         │
│                  SEGUNDO CLICK AQUÍ → ✕                │
│                  🎯 Esquina inferior derecha           │
│                  📍 Antes del borde de BlueStacks      │
└─────────────────────────────────────────────────────────┘
```

### Detalles Importantes

#### ✅ PRIMER CLICK (Esquina Superior Izquierda):
```
┌─────────────────────────────────────
│ ⚙️ BlueStacks                    
├─────────────────────────────────────  ← BARRA AQUÍ
│ 
│ ✕ ← CLICK AQUÍ (5-10 píxeles hacia adentro)
│    📍 Coordenadas ejemplo: (50, 50) relativo al borde
│ 
│    ⚠️ NO en la barra de título
│    ⚠️ NO en los bordes de la ventana
│    ⚠️ SÍ dentro del área de juego
```

**¿Por qué no en el borde exacto?**
- Los bordes de ventana pueden tener efectos visuales
- Puede haber áreas no-clickeables
- 5-10 píxeles hacia adentro asegura que estamos en el juego

#### ✅ SEGUNDO CLICK (Esquina Inferior Derecha):
```
│                                     
│                                     
│                                     
│                          ✕ ← CLICK AQUÍ
│                          📍 5-10 píxeles antes del borde
│    
└─────────────────────────────────────
  ⚠️ NO en el borde exacto
  ⚠️ SÍ dentro del área de juego
```

---

## 🔧 Proceso de Calibración Paso a Paso

### Paso 1: Preparar BlueStacks

1. ✅ Abre BlueStacks
2. ✅ Inicia Jurassic World Alive
3. ✅ Ve al **mapa principal** (donde ves supply drops, dinosaurios, etc.)
4. ✅ Espera a que cargue completamente
5. ✅ **NO muevas la ventana de BlueStacks después de este punto**

### Paso 2: Ejecutar el Bot

```bash
# En Windows PowerShell o CMD:
python main.py

# En Mac/Linux Terminal:
python3 main.py
```

**Deberías ver:**
```
[2026-01-19 14:30:00] [INFO] ================================================================================
[2026-01-19 14:30:00] [INFO] 🦖 JURASSIC WORLD ALIVE BOT - INICIADO
[2026-01-19 14:30:00] [INFO] ================================================================================
[2026-01-19 14:30:00] [INFO] 📁 Log guardado en: logs/bot_log_20260119_143000.log
[2026-01-19 14:30:00] [INFO] 🔧 Inicializando Bot...
[2026-01-19 14:30:00] [INFO] 📁 Carpeta 'debug_screenshots' creada
Press 'q' to quit.
```

### Paso 3: Primer Click (Esquina Superior Izquierda)

1. **Presiona la tecla 'a'** (una vez)
2. Verás en consola:
   ```
   KEY PRESSED
   ```
3. **Mueve el mouse** a la esquina superior izquierda del JUEGO
4. **Click** en esa posición
5. El bot registra las coordenadas automáticamente

```
📍 EJEMPLO DE POSICIÓN:
   Si BlueStacks está en (100, 100) de tu pantalla
   Y clickeas 10 píxeles adentro del juego
   → Se guarda: x=110, y=110
```

### Paso 4: Segundo Click (Esquina Inferior Derecha)

1. **Presiona la tecla 'a'** (segunda vez)
2. Verás en consola:
   ```
   KEY PRESSED
   ```
3. **Mueve el mouse** a la esquina inferior derecha del JUEGO
4. **Click** en esa posición
5. El bot calcula automáticamente el ancho y alto

```
📍 EJEMPLO DE CÁLCULO:
   Primer click: (110, 110)
   Segundo click: (1510, 810)
   
   → Ancho (w) = 1510 - 110 = 1400 píxeles
   → Alto (h) = 810 - 110 = 700 píxeles
```

### Paso 5: Verificar Configuración

Deberías ver en la consola y en el log:

```
[2026-01-19 14:30:15] [INFO] ================================================================================
[2026-01-19 14:30:15] [INFO] 📐 CONFIGURACIÓN DE VENTANA BLUESTACKS
[2026-01-19 14:30:15] [INFO] ================================================================================
[2026-01-19 14:30:15] [INFO] 📍 Posición X: 110px
[2026-01-19 14:30:15] [INFO] 📍 Posición Y: 110px
[2026-01-19 14:30:15] [INFO] 📏 Ancho (W): 1400px
[2026-01-19 14:30:15] [INFO] 📏 Alto (H): 700px
[2026-01-19 14:30:15] [INFO] 🎯 Esquina superior izquierda: (110, 110)
[2026-01-19 14:30:15] [INFO] 🎯 Esquina inferior derecha: (1510, 810)
[2026-01-19 14:30:15] [INFO] ================================================================================
[2026-01-19 14:30:15] [INFO] 🎯 Shooting zone: Y[161-489] X[14-574]
[2026-01-19 14:30:15] [INFO] 🚀 Launch button: Y[549-601] X[185-435]
[2026-01-19 14:30:15] [INFO] 📝 Supply text area: Y[126-210] X[112-560]
```

---

## ✅ Verificación de Coordenadas

### ¿Cómo saber si calibraste correctamente?

#### Método 1: Revisar los Logs

Busca estas líneas en el log:

```
📏 Ancho (W): XXXXX px
📏 Alto (H): XXXXX px
```

**Valores esperados según resolución:**

| Resolución BlueStacks | Ancho Esperado | Alto Esperado |
|-----------------------|----------------|---------------|
| 1600x900 | ~1550-1600 | ~850-900 |
| 1280x720 | ~1230-1280 | ~670-720 |
| Personalizado | (depende de tu config) | (depende de tu config) |

**⚠️ Si tus valores son muy diferentes:**
- Puede que hayas clickeado en los bordes de la ventana
- Puede que la ventana esté en modo pantalla completa
- Puede que hayas clickeado fuera del área del juego

#### Método 2: Verificar Zonas Calculadas

El bot calcula automáticamente las zonas de interés. Verifica que sean razonables:

```
🎯 Shooting zone: Y[XXX-XXX] X[XXX-XXX]
```

**Ejemplo de buena calibración:**
```
🎯 Shooting zone: Y[161-489] X[14-574]
→ Altura de zona: 489-161 = 328 píxeles ✅
→ Ancho de zona: 574-14 = 560 píxeles ✅
```

**Ejemplo de mala calibración:**
```
🎯 Shooting zone: Y[10-20] X[5-15]
→ Zona muy pequeña ❌
→ Probablemente clickeaste mal
```

---

## 📊 Interpretación de Logs

### Tipos de Mensajes en los Logs

#### 🟢 [INFO] - Información General
```
[INFO] 🦖 JURASSIC WORLD ALIVE BOT - INICIADO
[INFO] 📍 Posición X: 110px
```
Mensajes normales de operación. Todo va bien.

#### 🔵 [DEBUG] - Información Detallada
```
[DEBUG] 🔍 Buscando supply drops...
[DEBUG]    📊 Supply color range: R[160-255] G[60-255] B[0-120]
```
Información técnica para debugging. Solo visible si activas modo DEBUG.

#### 🟡 [WARNING] - Advertencias
```
[WARNING] ❌ [ESTADO DETECTADO] NO IDENTIFICADO - OCR puede haber fallado
```
Algo no salió como esperado, pero el bot puede continuar.

#### 🔴 [ERROR] - Errores
```
[ERROR] No se pudo capturar pantalla
```
Error que puede detener el bot.

### Logs Importantes para Calibración

#### 1. Configuración de Ventana
```
[INFO] ================================================================================
[INFO] 📐 CONFIGURACIÓN DE VENTANA BLUESTACKS
[INFO] ================================================================================
[INFO] 📍 Posición X: 110px       ← Coordenada X de la esquina sup. izq.
[INFO] 📍 Posición Y: 110px       ← Coordenada Y de la esquina sup. izq.
[INFO] 📏 Ancho (W): 1400px       ← Ancho de la ventana del juego
[INFO] 📏 Alto (H): 700px         ← Alto de la ventana del juego
```

**¿Qué verificar?**
- ✅ Ancho y Alto deben ser similares a la resolución de BlueStacks
- ✅ Posición X e Y deben estar dentro de tu pantalla

#### 2. Zonas de Detección
```
[INFO] 🎯 Shooting zone: Y[161-489] X[14-574]
```
**Cálculo:**
- Y_min = 161 = (230/831) * 700
- Y_max = 489 = (740/971) * 700  ← Nota: usa ratio diferente
- X_min = 14 = (10/481) * 1400
- X_max = 574 = (410/481) * 1400

**¿Es correcto?**
- ✅ La altura debe ser ~60-70% del alto total
- ✅ El ancho debe ser ~40-45% del ancho total

#### 3. Detección de Supply Drops
```
[DEBUG] 🔍 Buscando supply drops...
[DEBUG]    📊 Supply color range: R[160-255] G[60-255] B[0-120]
[DEBUG]    📐 Zona analizada: (328, 560, 3)
[DEBUG]    🎨 Píxeles detectados inicialmente: 1234
[DEBUG]    🔢 Componentes detectados: 3
[DEBUG]    ✅ Supply drop #1: 156 píxeles en posición (300, 250)
[DEBUG]    ✅ Supply drop #2: 203 píxeles en posición (400, 350)
[DEBUG]    ✅ Supply drop #3: 187 píxeles en posición (250, 450)
[INFO] 🟠 [SUPPLY DROP] Detectados 3 supply drops: [[300, 250], [400, 350], [250, 450]]
```

**¿Qué significan estos números?**

- **Zona analizada (328, 560, 3):**
  - 328 píxeles de alto
  - 560 píxeles de ancho
  - 3 canales de color (RGB)

- **Píxeles detectados inicialmente: 1234:**
  - Cantidad de píxeles que coinciden con los rangos de color
  - Si es 0 → No se detectan colores (calibrar colores)
  - Si es >10000 → Muchos falsos positivos (ajustar rangos)

- **Componentes detectados: 3:**
  - Número de objetos separados encontrados
  - Cada componente es un posible supply drop

- **Supply drop #1: 156 píxeles en posición (300, 250):**
  - Tamaño: 156 píxeles (debe ser >10 para ser válido)
  - Posición: (Y=300, X=250) en coordenadas de pantalla

#### 4. OCR y Detección de Estado
```
[DEBUG] 🔍 Determinando estado del objeto...
[DEBUG]    📐 Área botón lanzar: (62, 178, 3)
[DEBUG]    📐 Área texto supply: (100, 320, 3)
[INFO] 📝 [OCR] Botón: 'LANZAR'
[INFO] 📝 [OCR] Texto: 'SUMINISTRO'
[INFO] 📝 [OCR] Combinado: 'LANZAR SUMINISTRO'
[DEBUG]    📦 Palabras clave de SUPPLY detectadas
[INFO] ✅ [ESTADO DETECTADO] SUPPLY
```

**¿Qué verificar?**

- **Área botón lanzar: (62, 178, 3):**
  - 62 píxeles de alto
  - 178 píxeles de ancho
  - Si es muy pequeño (<50 píxeles), puede fallar el OCR

- **OCR Texto:**
  - Si muestra caracteres raros: "L4NZ4R", "5UM1N1STR0"
    → OCR está confundiendo letras con números
    → Puede ser problema de calidad de imagen
  
  - Si muestra vacío: ""
    → El área capturada no tiene texto
    → Ajustar `supply_drop_text_loc_ratio`

---

## 🐛 Troubleshooting

### Problema 1: "No se detectan supply drops"

#### Síntomas:
```
[DEBUG] 🔍 Buscando supply drops...
[DEBUG]    🎨 Píxeles detectados inicialmente: 0
[DEBUG]    ❌ No se detectaron supply drops
```

#### Soluciones:

**A) Verificar colores RGB**
1. Abre el log y busca:
   ```
   [DEBUG]    📊 Supply color range: R[XXX-XXX] G[XXX-XXX] B[XXX-XXX]
   ```
2. Toma una captura de pantalla con supply drop visible
3. Usa un color picker para verificar los colores
4. Ajusta en `jw_bot.py` si es necesario

**B) Verificar zona de búsqueda**
1. Busca en el log:
   ```
   [INFO] 🎯 Shooting zone: Y[XXX-XXX] X[XXX-XXX]
   ```
2. Verifica que cubra el área central del mapa
3. Si es muy pequeña, recalibra con 'a' + 'a'

**C) Reducir umbral de píxeles**
En `jw_bot.py` línea ~333, cambia:
```python
if len(rows) > 10:  # Probar con 5 o incluso 3
```

### Problema 2: "OCR no reconoce texto"

#### Síntomas:
```
[INFO] 📝 [OCR] Botón: ''
[INFO] 📝 [OCR] Texto: ''
[WARNING] ❌ [ESTADO DETECTADO] NO IDENTIFICADO
```

#### Soluciones:

**A) Verificar área de captura**
1. Busca en el log:
   ```
   [DEBUG]    📐 Área botón lanzar: (62, 178, 3)
   [DEBUG]    📐 Área texto supply: (100, 320, 3)
   ```
2. Si algún valor es muy pequeño (<50), ajustar ratios

**B) Activar debug visual**
1. Descomenta en `jw_bot.py` línea ~1034:
   ```python
   self.debug_save_ocr_regions(background_new, f"supply_{pos[0]}_{pos[1]}")
   ```
2. Ejecuta bot
3. Revisa carpeta `debug_screenshots/`
4. Verifica que las imágenes capturen texto correctamente

**C) Verificar instalación de Tesseract**
```bash
# Windows CMD
tesseract --version

# Mac/Linux Terminal
tesseract --version
```

Si no está instalado, ver guía de instalación.

### Problema 3: "El bot hace clicks en posiciones incorrectas"

#### Síntomas:
- Clicks fuera de la ventana de BlueStacks
- Clicks en posiciones aleatorias
- No clickea donde hay supply drops

#### Soluciones:

**A) Recalibrar completamente**
1. Cierra el bot (presiona 'q')
2. **NO MUEVAS** la ventana de BlueStacks
3. Ejecuta `python main.py` otra vez
4. Presiona 'a' + click esquina superior izquierda
5. Presiona 'a' + click esquina inferior derecha
6. Verifica logs de configuración

**B) Verificar que BlueStacks no se movió**
1. Busca en el log anterior:
   ```
   [INFO] 📍 Posición X: 110px
   [INFO] 📍 Posición Y: 110px
   ```
2. Si BlueStacks se movió, esas coordenadas ya no son válidas
3. Recalibra

**C) Desactivar efectos visuales de Windows**
- Los efectos de transparencia/sombra pueden afectar detección
- Configura BlueStacks en modo "ventana sin bordes" si es posible

### Problema 4: "Valores de calibración parecen incorrectos"

#### Síntomas:
```
[INFO] 📏 Ancho (W): 50px      ← ❌ Demasiado pequeño
[INFO] 📏 Alto (H): 30px       ← ❌ Demasiado pequeño
```

#### Causas:
- Clickeaste dos veces en el mismo lugar
- Clickeaste en orden inverso (primero abajo, luego arriba)
- Clickeaste fuera de la ventana

#### Solución:
```
1. Reinicia el bot
2. Al presionar 'a' la PRIMERA vez → Click ARRIBA-IZQUIERDA
3. Al presionar 'a' la SEGUNDA vez → Click ABAJO-DERECHA
4. Asegúrate de que:
   - El segundo click esté MÁS ABAJO que el primero
   - El segundo click esté MÁS A LA DERECHA que el primero
```

---

## 📁 Ubicación de Archivos de Log

Los logs se guardan automáticamente en:

```
jwa_bot/
├── logs/
│   ├── bot_log_20260119_143000.log  ← Log de sesión 1
│   ├── bot_log_20260119_150000.log  ← Log de sesión 2
│   └── bot_log_20260119_160000.log  ← Log de sesión 3
├── debug_screenshots/                ← Screenshots de debug
│   ├── supply_300_250_launch_button.png
│   ├── supply_300_250_supply_text.png
│   └── supply_300_250_full_screen.png
├── jw_bot.py
└── main.py
```

**Para enviar logs al desarrollador:**
1. Ve a la carpeta `logs/`
2. Encuentra el archivo más reciente (por timestamp)
3. Envía ese archivo .log completo

---

## ✅ Checklist de Calibración Exitosa

- [ ] BlueStacks con resolución fija (no pantalla completa)
- [ ] Ventana de BlueStacks completamente visible
- [ ] Juego Jurassic World Alive en el mapa principal
- [ ] Bot ejecutado: `python main.py`
- [ ] Presionar 'a' → Click esquina superior izquierda DEL JUEGO
- [ ] Presionar 'a' → Click esquina inferior derecha DEL JUEGO
- [ ] Ver en log: "📐 CONFIGURACIÓN DE VENTANA BLUESTACKS"
- [ ] Ancho (W) es ~1200-1600 px (según resolución)
- [ ] Alto (H) es ~650-900 px (según resolución)
- [ ] Shooting zone calculada correctamente
- [ ] Ver en log: "🎯 Shooting zone: Y[XXX-XXX] X[XXX-XXX]"

**Si todos los checks están ✅, la calibración fue exitosa!**

---

## 📸 Ejemplo Visual Completo

```
ANTES DE CALIBRAR:
==================
Ventana BlueStacks en pantalla
Mouse listo para primer click

┌─────────────────────────────────────────┐
│ ⚙️ BlueStacks            [─][□][✕]     │
├─────────────────────────────────────────┤
│                                         │
│  🖱️ CLICK AQUÍ (primer 'a')            │
│  ↓                                      │
│  ✕ (5px adentro)                       │
│                                         │
│        JURASSIC WORLD ALIVE             │
│           (Mapa visible)                │
│                                         │
│                                         │
│                         ✕ 🖱️ CLICK     │
│                         (segundo 'a')   │
└─────────────────────────────────────────┘


DESPUÉS DE CALIBRAR:
====================
Log muestra:

[INFO] 📐 CONFIGURACIÓN DE VENTANA BLUESTACKS
[INFO] 📍 Posición X: 50px
[INFO] 📍 Posición Y: 100px
[INFO] 📏 Ancho (W): 1550px
[INFO] 📏 Alto (H): 870px
[INFO] 🎯 Esquina superior izquierda: (50, 100)
[INFO] 🎯 Esquina inferior derecha: (1600, 970)

✅ Bot configurado correctamente!
```

---

**Última actualización:** 19 de enero de 2026  
**Versión:** 3.0 (Sistema de Logging Completo)
