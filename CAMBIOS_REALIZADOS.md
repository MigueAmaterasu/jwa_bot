# 🔧 Cambios Realizados al Bot de Jurassic World Alive

## 📋 Problemas Identificados y Soluciones

### ❌ **Problema 1: No recoge suministros (supply drops ni eventos)**

#### Causas identificadas:
1. **Umbral de píxeles muy alto** - Filtraba supply drops pequeños
2. **Prints de debug excesivos** - Ralentizaban la ejecución
3. **No detectaba eventos como supply drops** - Solo buscaba "supply" exacto
4. **Tiempos de espera muy cortos** - OCR no tenía tiempo de procesar

#### ✅ Soluciones aplicadas:
- **Línea ~257**: Reducido umbral de `len(rows) > 20` a `len(rows) > 10` para detectar supply drops más pequeños
- **Línea ~243-280**: Eliminados prints de debug excesivos, solo se muestra cantidad detectada
- **Línea ~922**: Ahora acepta tanto `state == "supply"` como `state == "event"` 
- **Línea ~910**: Aumentado tiempo de espera de 0.8s a 1.0s para dar más tiempo al OCR
- **Línea ~913**: Aumentado tiempo de espera de 0.2s a 0.3s después de click
- **Línea ~930**: Aumentado tiempo de espera de 2s a 2.5s para activar supply drop

---

### ❌ **Problema 2: Solo lanza 2-3 dardos como máximo**

#### Causas identificadas:
1. **Timeout muy corto** - 60 segundos no era suficiente para dinosaurios móviles
2. **Bug en cálculo de batería** - Se invertía dos veces el valor (double negative)
3. **Detección de loading screen fallaba** - Salía del loop prematuramente

#### ✅ Soluciones aplicadas:
- **Línea ~700**: Incrementado timeout de **60 a 120 segundos** en bucle principal de disparo
- **Línea ~756**: Actualizado timeout de 60 a 120 en verificación final
- **Línea ~641**: Corregida función `get_battery_left()` para retornar correctamente (0=vacía, 1=llena)
- **Línea ~719**: Eliminada la inversión duplicada `battery_left = 1 - self.get_battery_left()`
  - **Antes**: `battery_left = 1 - self.get_battery_left(background)` ❌
  - **Ahora**: `battery_left = self.get_battery_left(background)` ✅

---

### ⚡ **Problema 3: Detección OCR mezclada español/inglés**

#### Causas identificadas:
1. **Palabras mezcladas sin prioridad** - Español e inglés al mismo nivel
2. **Faltaban variantes en español** - "SUMINISTRO" completo no se detectaba
3. **Outputs de debug poco claros** - Difícil saber qué detectaba el OCR

#### ✅ Soluciones aplicadas:
- **Línea ~450-480**: Mejorada función `determine_state()` con prioridad español
  - Agregadas palabras: "EVENTO", "SUMINISTRO", "MONEDAS", "DINO"
  - Output mejorado: `[OCR] Botón: 'LANZAR' | Texto: 'SUMINISTRO'`
  - Muestra estado detectado: `[ESTADO DETECTADO] SUPPLY`

---

### 🎯 **Mejoras Adicionales**

#### 1. **Detección de monedas más sensible**
- **Línea ~298**: Reducido umbral de 15 a 10 píxeles
- Agregado mensaje: `[COINS] Detectadas X monedas`

#### 2. **Threshold de cambio de fondo ajustado**
- **Línea ~968**: Reducido de 2000 a 1500 para ser más sensible
- Mejorado output: `[DIFF] 1234.5 (threshold: 1500)`

#### 3. **Configuración de Tesseract más clara**
- **Línea ~11-22**: Agregada documentación detallada
- Configuración comentada por defecto (asume que Tesseract está en PATH)
- Instrucciones para Windows y macOS

#### 4. **Mensajes de debug más informativos**
- Supply drops: `[SUPPLY DROP] Detectados X supply drops`
- Clicks: `CLICK 1/4` (muestra progreso)
- Estados: `NOT SUPPLY DROP (detected: coin)` (muestra qué detectó)

---

## 🚀 Cómo Probar las Mejoras

### 1. **Configurar Tesseract**
Asegúrate de que Tesseract OCR esté instalado y en el PATH del sistema.

Si no está en el PATH, descomenta y ajusta la línea en `jw_bot.py`:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
```

### 2. **Verificar coordenadas de BlueStacks**
Al iniciar el bot, presiona 'a' dos veces para definir el área del emulador:
1. Primera presión: esquina superior izquierda
2. Segunda presión: esquina inferior derecha

### 3. **Monitorear los nuevos mensajes**
Observa la consola para ver:
- `[SUPPLY DROP] Detectados X supply drops`
- `[COINS] Detectadas X monedas`
- `[OCR] Botón: 'LANZAR' | Texto: 'SUMINISTRO'`
- `[ESTADO DETECTADO] SUPPLY`
- `CLICK 1/4` (progreso de clicks)

### 4. **Ajustes finos según tu configuración**

Si aún no detecta supply drops, puedes ajustar en `jw_bot.py`:

```python
# Línea ~257 - Reducir más el umbral si es necesario
if len(rows) > 5:  # Cambia de 10 a 5 para ser más agresivo

# Línea ~968 - Reducir threshold si clicks no se registran
def background_changed(self, b1, b2, threshold=1000):  # Cambia de 1500 a 1000
```

---

## 📊 Resumen de Cambios Numéricos

| Parámetro | Antes | Después | Motivo |
|-----------|-------|---------|--------|
| Timeout disparo | 60s | 120s | Dinosaurios móviles necesitan más tiempo |
| Umbral supply drops | 20 px | 10 px | Detectar supply drops más pequeños |
| Umbral monedas | 15 px | 10 px | Detectar monedas más pequeñas |
| Espera post-click | 0.2s | 0.3s | Dar tiempo a la animación |
| Espera OCR | 0.8s | 1.0s | OCR necesita más tiempo |
| Threshold background | 2000 | 1500 | Más sensible a cambios |
| Batería invertida | Sí ❌ | No ✅ | Cálculo correcto |

---

## 🐛 Debugging

Si algo sigue sin funcionar, revisa estos puntos:

1. **Supply drops no detectados**: 
   - Verifica que los colores RGB en las líneas 70-85 coincidan con tu juego
   - Puedes usar un color picker para obtener los colores exactos de tu pantalla

2. **OCR no reconoce texto**:
   - Asegúrate de que Tesseract esté instalado correctamente
   - Prueba cambiar el idioma: `pytesseract.image_to_string(image, lang='spa')`

3. **Bot hace clicks en lugares incorrectos**:
   - Recalibra las coordenadas con 'a' + 'a'
   - Verifica que la resolución de BlueStacks no haya cambiado

4. **Solo dispara pocos dardos**:
   - Aumenta aún más el timeout en línea ~700 (ej: 180 segundos)
   - Verifica que el `loading_screen.png` en `/figs/` sea correcto

---

## ✅ Checklist Pre-Ejecución

- [ ] Tesseract OCR instalado y configurado
- [ ] BlueStacks ejecutándose con Jurassic World Alive abierto
- [ ] Juego en español (o ajustar palabras en `determine_state()`)
- [ ] Carpeta `/figs/` existe con `loading_screen.png`
- [ ] Calibrar coordenadas del emulador con 'a' + 'a'
- [ ] Presionar 'q' para detener el bot de forma segura

---

**Fecha de modificaciones**: 19 de enero de 2026
**Versión**: 2.0 (Mejorada)
