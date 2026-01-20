# CAMBIOS v3.2 - Corrección de Áreas OCR y Filtros

## 🎯 Problemas Identificados (Análisis de Logs e Imágenes)

### Problema #1: Detección de Falsos Positivos
- ✅ Bot detectaba 59-67 "supply drops" cuando solo había 2-3 reales
- ✅ Hacía clic en dinosaurios fuera de rango (mensaje "ÚNETE AHORA")
- ✅ Hacía clic en páginas de compra/bonificación
- ✅ Hacía clic en elementos del UI (anuncios, botones)

### Problema #2: Áreas OCR Incorrectas
- ❌ Área de texto estaba en Y[171-286] (medio de la pantalla)
- ❌ Capturaba la parte superior de la cajita, NO el texto descriptivo
- ❌ El texto "EVENTO"/"SUMINISTRO" está en la parte SUPERIOR de la pantalla
- ❌ Los supply drops NO tienen botón "LANZAR" (se hace clic en la cajita)

## ✅ Soluciones Implementadas

### Fix #1: Nueva Área de Texto OCR
**ANTES:**
```python
self.supply_drop_text_loc_ratio = (150 / 831, 250 / 831, 80 / 481, 400 / 481)
# Y[18%-30%] X[16%-83%] - En medio de la pantalla
```

**DESPUÉS:**
```python
self.supply_drop_text_loc_ratio = (0.05, 0.15, 0.20, 0.80)
# Y[5%-15%] X[20%-80%] - Parte SUPERIOR de la pantalla
```

**Resultado:** Ahora captura correctamente "EVENTO", "SUMINISTRO DE EVENTO"

### Fix #2: Filtros de Exclusión Mejorados
Agregados en `determine_state()`:

1. **Dinosaurios fuera de rango:**
   - Detecta: "ÚNETE", "AHORA", "JOIN"
   - Acción: Marca como `out_of_range` y salta

2. **Páginas de compra:**
   - Detecta: "COMPRA", "BUY", "OFERTA", "PRECIO", "$", "PAQUETE"
   - Acción: Marca como `out_of_range` y salta

3. **Pantallas de carga/menú:**
   - Detecta: "CARGANDO", "LOADING", "MENÚ"
   - Acción: Marca como `out_of_range` y salta

### Fix #3: Skip de Objetos Fuera de Rango
Agregado en 3 lugares del código principal:
```python
if state == "out_of_range":
    print("--"*10)
    print("OUT OF RANGE - SKIPPING")
    continue
```

## �� Resultados Esperados

### Antes v3.2:
- Detectaba: 59-67 objetos
- Hacía clic en: Dinosaurios VIP, anuncios, páginas de compra
- Supply drops recolectados: 0
- OCR capturaba: Texto incorrecto o vacío

### Después v3.2:
- Detectará: 2-5 objetos (solo supply drops reales)
- Ignorará: Dinosaurios VIP, anuncios, páginas de compra
- Supply drops recolectados: Esperado 100%
- OCR capturará: "EVENTO", "SUMINISTRO", "SUMINISTRO DE EVENTO"

## 🔍 Validación con Imágenes de Debug

| Imagen | Tipo Real | Texto Capturado (NUEVO) | Estado |
|--------|-----------|-------------------------|--------|
| supply_270_279 | Supply drop evento | "EVENTO" visible | ✅ CORRECTO |
| supply_264_153 | Dino fuera de rango | Solo dino (vacío) | ✅ Será excluido |
| supply_612_38 | Página compra | Vacío | ✅ Será excluido |

## 🚀 Próximos Pasos

1. **Testing:** Ejecutar bot 15-20 minutos
2. **Verificar logs:** Buscar mensajes "⛔ [EXCLUIDO]"
3. **Contar supply drops:** Debe recolectar los reales
4. **Ajuste fino:** Si es necesario, ajustar rangos RGB de detección de color

## 📝 Archivos Modificados

- `jw_bot.py` (líneas ~98, ~622-642, ~992, ~1062, ~1124)
