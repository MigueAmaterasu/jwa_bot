# 🎨 Guía de Colores y Calibración - Bot JWA

## 📋 Índice
1. [Problemas Corregidos](#problemas-corregidos)
2. [Colores RGB Configurados](#colores-rgb-configurados)
3. [Cómo Calibrar Colores](#cómo-calibrar-colores)
4. [Área de OCR Corregida](#área-de-ocr-corregida)
5. [Debug y Troubleshooting](#debug-y-troubleshooting)

---

## 🔧 Problemas Corregidos

### ❌ **Problema Identificado #1: Área de OCR Incorrecta**

**ANTES:**
```python
self.supply_drop_text_loc_ratio = (92 / 831, 132 / 831, 110 / 481, 330 / 481)
# Área: 40 píxeles de alto (92-132) ❌ MUY PEQUEÑA
```

**DESPUÉS:**
```python
self.supply_drop_text_loc_ratio = (150 / 831, 250 / 831, 80 / 481, 400 / 481)
# Área: 100 píxeles de alto (150-250) ✅ ÁREA CORRECTA
# Cubre la zona central-superior donde aparece el texto descriptivo
```

**Explicación:**
- El área anterior era demasiado pequeña y estaba posicionada incorrectamente
- Estaba buscando donde debería estar un BOTÓN, no el TEXTO descriptivo
- El nuevo área captura correctamente el nombre del objeto (SUMINISTRO, EVENTO, etc.)

### ❌ **Problema Identificado #2: Detección de Estado Inflexible**

**ANTES:**
- Solo buscaba en `text1` O `text2` por separado
- Si el OCR fallaba en una región, no detectaba nada
- Solo buscaba palabras exactas

**DESPUÉS:**
- ✅ Busca en TEXTO COMBINADO (text1 + text2)
- ✅ Prioridad: DINO > SUPPLY > EVENT > COIN
- ✅ Acepta palabras completas Y fragmentos parciales
- ✅ Convierte todo a UPPERCASE para evitar problemas de mayúsculas/minúsculas

---

## 🎨 Colores RGB Configurados

### Formato de Colores
```python
(R_min, G_min, B_min, R_max, G_max, B_max)
```
Los píxeles que caigan dentro de este rango en RGB serán detectados como ese objeto.

### 🟠 Supply Drops Normales (ACTIVO)
```python
self.supply_drop_color = (160, 60, 0, 255, 255, 120)
```
- **Rango R (Rojo):** 160-255 ⬆️ Alto
- **Rango G (Verde):** 60-255 ⬆️ Alto  
- **Rango B (Azul):** 0-120 ⬇️ Bajo
- **Color resultante:** 🟠 Naranja/Amarillo brillante

### 🟢 Eventos Especiales (ACTIVO)
```python
self.special_event_color = (0, 120, 0, 180, 255, 180)
```
- **Rango R (Rojo):** 0-180 ⬇️ Bajo
- **Rango G (Verde):** 120-255 ⬆️ Muy Alto
- **Rango B (Azul):** 0-180 ⬇️ Bajo
- **Color resultante:** 🟢 Verde brillante

### 🟡 Monedas / Coin Chase (ACTIVO)
```python
self.coin_color = (180, 160, 100, 240, 220, 120)
```
- **Rango R (Rojo):** 180-240 ⬆️ Alto
- **Rango G (Verde):** 160-220 ⬆️ Alto
- **Rango B (Azul):** 100-120 ➡️ Medio-Bajo
- **Color resultante:** 🟡 Dorado brillante

### ❌ Botón X (Cerrar)
```python
self.x_button_color = (117, 10, 10)
```
- **Color exacto:** Rojo oscuro (RGB: 117, 10, 10)

### 🔋 Batería de Dardos
```python
self.battery_color = (10, 30, 80)
```
- **Color exacto:** Azul oscuro (RGB: 10, 30, 80)

---

## 🎨 Colores Alternativos para Eventos

### 🧧 Año Nuevo Lunar (Lunar New Year)
```python
# Descomentar estas líneas en jw_bot.py:
self.special_event_color = (170, 140, 50, 230, 190, 100)
self.supply_drop_color = (150, 120, 0, 255, 180, 60)
self.coin_color = (200, 50, 20, 255, 140, 50)
```

### 💝 San Valentín (Valentine's Day)
```python
# Descomentar estas líneas en jw_bot.py:
self.special_event_color = (0, 140, 0, 100, 255, 100)
self.supply_drop_color = (180, 0, 0, 255, 100, 120)
self.coin_color = (180, 0, 0, 255, 100, 120)
```

### ❄️ Invierno / St. Petersburg
```python
# Descomentar estas líneas en jw_bot.py:
self.special_event_color = (0, 140, 0, 45, 255, 45)
self.supply_drop_color = (60, 60, 0, 210, 210, 120)
self.coin_color = (20, 35, 130, 95, 95, 170)  # Azul
```

---

## 🔍 Cómo Calibrar Colores

Si el bot **NO DETECTA** supply drops, eventos o monedas, necesitas calibrar los colores:

### Método 1: Color Picker Manual

#### Paso 1: Tomar Captura de Pantalla
1. Abre BlueStacks con Jurassic World Alive
2. Ve al mapa donde se vean supply drops / eventos / monedas
3. Toma una captura de pantalla (Win + Shift + S en Windows, Cmd + Shift + 4 en Mac)

#### Paso 2: Obtener Valores RGB
1. Abre la captura en un editor de imágenes:
   - **Windows:** Paint, GIMP, Photoshop
   - **Mac:** Preview, GIMP, Photoshop
   - **Online:** https://imagecolorpicker.com/

2. Usa la herramienta **Color Picker / Cuentagotas**

3. Click en el objeto que quieres detectar (supply drop, moneda, etc.)

4. Anota los valores RGB:
   ```
   Ejemplo: R=245, G=180, B=60  (supply drop naranja)
   ```

#### Paso 3: Calcular Rangos
Necesitas definir un RANGO, no un color exacto:

```python
# Si tu color muestra es RGB: (245, 180, 60)
# Crea un rango tolerante:

R_min = 245 - 40 = 205
R_max = 245 + 10 = 255  # Máximo es 255

G_min = 180 - 40 = 140
G_max = 180 + 40 = 220

B_min = 60 - 30 = 30
B_max = 60 + 30 = 90

# Resultado:
self.supply_drop_color = (205, 140, 30, 255, 220, 90)
```

**💡 Regla General:**
- **Componente dominante** (más alto): Rango amplio (-40 a +10)
- **Componentes bajos**: Rango estrecho (-30 a +30)

#### Paso 4: Actualizar en jw_bot.py

Busca la sección de colores (línea ~70-150) y actualiza:

```python
# ========================================================================
# CONFIGURACIÓN DE COLORES RGB PARA DETECCIÓN
# ========================================================================

# 🟠 SUPPLY DROPS - TUS VALORES AQUÍ
self.supply_drop_color = (205, 140, 30, 255, 220, 90)

# 🟢 EVENTOS ESPECIALES - TUS VALORES AQUÍ
self.special_event_color = (0, 120, 0, 180, 255, 180)

# 🟡 MONEDAS - TUS VALORES AQUÍ
self.coin_color = (180, 160, 100, 240, 220, 120)
```

---

### Método 2: Función de Debug Automática

El bot ahora incluye una función de debug que GUARDA las imágenes que está capturando:

#### Paso 1: Habilitar Debug
En `jw_bot.py`, busca la función `collect_supply_drop` (línea ~990) y descomenta:

```python
# 🔍 DEBUG: Descomentar la siguiente línea para guardar imágenes de lo que ve el OCR
self.debug_save_ocr_regions(background_new, f"supply_{pos[0]}_{pos[1]}")
```

Debería quedar así:
```python
# 🔍 DEBUG: Descomentar la siguiente línea para guardar imágenes de lo que ve el OCR
self.debug_save_ocr_regions(background_new, f"supply_{pos[0]}_{pos[1]}")  # ✅ ACTIVADO
```

#### Paso 2: Ejecutar el Bot
- El bot guardará imágenes en la carpeta `debug_screenshots/`
- Se crearán 3 archivos por cada click:
  - `supply_XXX_YYY_launch_button.png` - Área del botón lanzar
  - `supply_XXX_YYY_supply_text.png` - Área del texto descriptivo
  - `supply_XXX_YYY_full_screen.png` - Pantalla completa

#### Paso 3: Revisar las Imágenes
1. Abre las imágenes guardadas en `debug_screenshots/`
2. Verifica que el área `supply_text.png` captura correctamente el texto "SUMINISTRO" o "EVENTO"
3. Si NO captura el texto correctamente:
   - Ajusta `self.supply_drop_text_loc_ratio` en línea ~35
   - Aumenta o mueve el área de captura

#### Paso 4: Obtener Colores de las Imágenes
1. Abre `full_screen.png` en un color picker
2. Click en el supply drop visible
3. Anota RGB y calcula rangos (ver Método 1, Paso 3)

---

## 📐 Área de OCR Corregida

### Visualización de Áreas

```
┌─────────────────────────────────────────┐
│         PANTALLA BLUESTACKS             │
│  ┌───────────────────────────────┐      │
│  │ 🔵 [150-250]  TEXTO AQUÍ      │ ← supply_drop_text_loc
│  │    "SUMINISTRO"               │   (Área NUEVA, más grande)
│  │    "EVENTO ESPECIAL"          │
│  │    "MONEDAS"                  │
│  └───────────────────────────────┘      │
│                                         │
│          (Área de juego)                │
│                                         │
│  ┌─────────────┐                        │
│  │   LANZAR    │ ← launch_button_loc   │
│  └─────────────┘   (650-712)           │
└─────────────────────────────────────────┘
```

### Coordenadas Actualizadas

```python
# ANTES ❌
self.supply_drop_text_loc = (92, 132, 110, 330)
# Altura: 132 - 92 = 40 píxeles ❌ MUY PEQUEÑA

# AHORA ✅
self.supply_drop_text_loc = (150, 250, 80, 400)
# Altura: 250 - 150 = 100 píxeles ✅ ÁREA ADECUADA
# Ancho: 400 - 80 = 320 píxeles ✅ CAPTURA TODO EL TEXTO
```

---

## 🐛 Debug y Troubleshooting

### Problema: "No detecta supply drops en el mapa"

**Posibles causas:**

1. **Colores RGB incorrectos**
   - ✅ Solución: Usar Método 1 o 2 de calibración
   - Verifica que los colores coincidan con tu pantalla/brillo

2. **Umbral de detección muy alto**
   - ✅ Solución: En línea ~260, cambiar:
   ```python
   if len(rows) > 10:  # Probar con 5 o incluso 3
   ```

3. **Resolución de BlueStacks diferente**
   - ✅ Solución: Recalibrar coordenadas con 'a' + 'a'
   - Asegurate de que la resolución sea consistente

### Problema: "Detecta supply drops pero no los recoge"

**Posibles causas:**

1. **OCR no reconoce el texto "SUMINISTRO"**
   - ✅ Solución: Habilitar debug (ver Método 2)
   - Verificar que `supply_text.png` capture el texto correctamente
   - Ajustar `supply_drop_text_loc_ratio` si es necesario

2. **Tesseract no instalado o mal configurado**
   - ✅ Solución: Verificar instalación de Tesseract
   - En Windows: Descomenta línea ~18 en `jw_bot.py`

3. **El estado se detecta como otro tipo**
   - ✅ Solución: Revisar los mensajes `[OCR]` en consola
   - Si dice "NOT SUPPLY DROP (detected: dino)", ajustar prioridades en `determine_state`

### Problema: "Los mensajes OCR muestran texto basura"

**Posibles causas:**

1. **Área de captura incorrecta**
   - ✅ Solución: Usar debug para ver qué captura
   - Ajustar `supply_drop_text_loc_ratio`

2. **Calidad de imagen baja**
   - ✅ Solución: Aumentar resolución de BlueStacks
   - Desactivar efectos gráficos que difuminen texto

3. **Idioma de Tesseract incorrecto**
   - ✅ Solución: En `determine_state`, cambiar:
   ```python
   text1 = pytesseract.image_to_string(launch_button, lang='spa', config=self.custom_config)
   ```

---

## 📊 Tabla Resumen de Colores

| Objeto | Color Visual | RGB Min | RGB Max | Activo |
|--------|--------------|---------|---------|--------|
| 🟠 Supply Drop Normal | Naranja | (160, 60, 0) | (255, 255, 120) | ✅ |
| 🟢 Evento Especial | Verde | (0, 120, 0) | (180, 255, 180) | ✅ |
| 🟡 Moneda | Dorado | (180, 160, 100) | (240, 220, 120) | ✅ |
| ❌ Botón X | Rojo Oscuro | (117, 10, 10) | N/A | ✅ |
| 🔋 Batería | Azul Oscuro | (10, 30, 80) | N/A | ✅ |
| 📍 GPS Location | Rojo | (200, 0, 0) | (255, 70, 60) | ✅ |

---

## ✅ Checklist de Calibración

- [ ] Tesseract OCR instalado y configurado
- [ ] BlueStacks con resolución fija (no cambiar durante uso)
- [ ] Captura de pantalla del juego con supply drops visibles
- [ ] Color picker para obtener RGB de supply drops
- [ ] Rangos RGB calculados y actualizados en `jw_bot.py`
- [ ] Debug habilitado para verificar áreas de OCR
- [ ] Revisar carpeta `debug_screenshots/` con resultados
- [ ] Ajustar `supply_drop_text_loc_ratio` si es necesario
- [ ] Verificar mensajes `[OCR]` en consola muestran texto correcto
- [ ] Confirmar que `[ESTADO DETECTADO] ✅ SUPPLY` aparece

---

## 🎯 Valores Recomendados por Configuración

### Para pantallas con brillo ALTO
```python
# Supply drops aparecen más brillantes
self.supply_drop_color = (180, 80, 0, 255, 255, 140)  # Rangos ampliados
```

### Para pantallas con brillo BAJO
```python
# Supply drops aparecen más opacos
self.supply_drop_color = (140, 40, 0, 240, 220, 100)  # Rangos reducidos
```

### Para BlueStacks en modo NOCHE
```python
# Colores más oscuros
self.supply_drop_color = (120, 30, 0, 200, 180, 80)
```

---

**Última actualización:** 19 de enero de 2026
**Versión:** 2.1 (Colores documentados y OCR corregido)
