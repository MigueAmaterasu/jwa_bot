#!/usr/bin/env python3
"""
Analiza características de dinos reales vs falsos positivos
y sugiere filtros para reducir 114 → ~10-20 detecciones
"""

import numpy as np
from skimage import filters, morphology, measure, io
from scipy import ndimage
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Cargar imagen
print("📸 Cargando imagen del mapa...")
background = io.imread('debug_screenshots/map_initial_20260131_164303.png')

# Definir shooting zone (misma que el bot)
shooting_zone = [230, 720, 10, 440]
background_cropped = background[shooting_zone[0]:shooting_zone[1],
                                shooting_zone[2]:shooting_zone[3]]

# Aplicar método Sobel actual
print("\n🔍 Aplicando Sobel edge detection...")
edges = filters.sobel(background_cropped)
mask = ((edges[:,:,0] <= 0.089) & 
        (edges[:,:,1] <= 0.089) & 
        (edges[:,:,2] <= 0.089))
mask = filters.median(mask, np.ones((3, 3)))
mask = morphology.binary_closing(mask, np.ones((5, 5)))
labels = measure.label(mask, background=0, connectivity=2)
dist = ndimage.distance_transform_edt(mask)

# Extraer propiedades de cada componente
print("\n📊 Analizando propiedades de componentes...")
regions = measure.regionprops(labels)

# Dinos confirmados por usuario (actualizado 31/01/2026 - verificados en imagen)
dinos_reales = {
    1: [609, 336],   # Más grande - 2107px
    2: [509, 329],   # Amarillo - 1827px
    11: [252, 288],  # Común - 287px
    12: [480, 10],   # Cortado mitad - 262px
    26: [341, 349],  # Dino - 69px
    27: [316, 413],  # Dino - 63px
}

# Analizar cada componente
detecciones = []
for region in regions:
    # Calcular centro usando distance transform (mismo método del bot)
    label_dist = dist * (labels == region.label).astype(np.uint8)
    row, col = np.unravel_index(label_dist.argmax(), label_dist.shape)
    
    # Extraer características
    area = region.area
    bbox = region.bbox  # (min_row, min_col, max_row, max_col)
    height = bbox[2] - bbox[0]
    width = bbox[3] - bbox[1]
    aspect_ratio = width / height if height > 0 else 0
    
    # Posición absoluta en mapa
    abs_row = shooting_zone[0] + row
    abs_col = shooting_zone[2] + col
    
    # Verificar si es dino real
    es_dino_real = False
    for num, pos in dinos_reales.items():
        if abs(abs_row - pos[0]) < 5 and abs(abs_col - pos[1]) < 5:
            es_dino_real = True
            break
    
    detecciones.append({
        'label': region.label,
        'pos': [abs_row, abs_col],
        'area': area,
        'height': height,
        'width': width,
        'aspect_ratio': aspect_ratio,
        'es_dino_real': es_dino_real,
        'bbox_rel': bbox  # Para visualizar
    })

# Ordenar por área (más grande primero)
detecciones.sort(key=lambda x: x['area'], reverse=True)

# Análisis estadístico
print("\n" + "="*70)
print("📈 ANÁLISIS DE CARACTERÍSTICAS")
print("="*70)

dinos = [d for d in detecciones if d['es_dino_real']]
falsos = [d for d in detecciones if not d['es_dino_real']]

print(f"\n✅ DINOS REALES (n={len(dinos)}):")
for d in dinos:
    print(f"   Pos [{d['pos'][0]}, {d['pos'][1]}] - Área: {d['area']}px, "
          f"Dimensiones: {d['width']}x{d['height']}, Ratio: {d['aspect_ratio']:.2f}")

if dinos:
    areas_dinos = [d['area'] for d in dinos]
    ratios_dinos = [d['aspect_ratio'] for d in dinos]
    print(f"\n   Área: min={min(areas_dinos)} max={max(areas_dinos)} media={np.mean(areas_dinos):.1f}")
    print(f"   Aspect ratio: min={min(ratios_dinos):.2f} max={max(ratios_dinos):.2f} media={np.mean(ratios_dinos):.2f}")

print(f"\n❌ FALSOS POSITIVOS (n={len(falsos)}) - Top 10 más grandes:")
for i, d in enumerate(falsos[:10], 1):
    print(f"   {i}. Pos [{d['pos'][0]}, {d['pos'][1]}] - Área: {d['area']}px, "
          f"Dimensiones: {d['width']}x{d['height']}, Ratio: {d['aspect_ratio']:.2f}")

if falsos:
    areas_falsos = [d['area'] for d in falsos]
    ratios_falsos = [d['aspect_ratio'] for d in falsos]
    print(f"\n   Área: min={min(areas_falsos)} max={max(areas_falsos)} media={np.mean(areas_falsos):.1f}")
    print(f"   Aspect ratio: min={min(ratios_falsos):.2f} max={max(ratios_falsos):.2f} media={np.mean(ratios_falsos):.2f}")

# Proponer filtros
print("\n" + "="*70)
print("🎯 FILTROS PROPUESTOS")
print("="*70)

# Análisis de área
print("\n1️⃣ FILTRO POR ÁREA:")
if dinos:
    min_area_dinos = min([d['area'] for d in dinos])
    max_area_dinos = max([d['area'] for d in dinos])
    
    # Margen de seguridad: 50% más bajo, 200% más alto (para dinos más grandes/lejos)
    filtro_min_area = int(min_area_dinos * 0.5)
    filtro_max_area = int(max_area_dinos * 3.0)
    
    falsos_filtrados_area = [d for d in falsos if filtro_min_area <= d['area'] <= filtro_max_area]
    print(f"   Dinos: {min_area_dinos}-{max_area_dinos}px")
    print(f"   Filtro propuesto: {filtro_min_area}-{filtro_max_area}px")
    print(f"   ✅ Conserva: {len(dinos)}/{len(dinos)} dinos reales")
    print(f"   ❌ Elimina: {len(falsos) - len(falsos_filtrados_area)}/{len(falsos)} falsos positivos")
    print(f"   ⚠️ Quedan: {len(falsos_filtrados_area)} falsos positivos")

# Análisis de aspect ratio
print("\n2️⃣ FILTRO POR ASPECT RATIO:")
if dinos:
    min_ratio_dinos = min([d['aspect_ratio'] for d in dinos])
    max_ratio_dinos = max([d['aspect_ratio'] for d in dinos])
    
    # Margen de seguridad: ±0.3
    filtro_min_ratio = max(0.3, min_ratio_dinos - 0.3)
    filtro_max_ratio = max_ratio_dinos + 0.3
    
    # Aplicar filtro combo (área + ratio)
    combo_filtrados = [d for d in falsos 
                       if (filtro_min_area <= d['area'] <= filtro_max_area) and 
                          (filtro_min_ratio <= d['aspect_ratio'] <= filtro_max_ratio)]
    
    print(f"   Dinos: {min_ratio_dinos:.2f}-{max_ratio_dinos:.2f}")
    print(f"   Filtro propuesto: {filtro_min_ratio:.2f}-{filtro_max_ratio:.2f}")
    print(f"   ✅ Conserva: {len(dinos)}/{len(dinos)} dinos reales")
    print(f"   ❌ Elimina (área + ratio): {len(falsos) - len(combo_filtrados)}/{len(falsos)} falsos positivos")
    print(f"   ⚠️ Quedan: {len(combo_filtrados)} falsos positivos")

# Análisis de posición
print("\n3️⃣ FILTRO POR POSICIÓN:")
# Sin filtro de bordes - los dinos pueden aparecer en cualquier parte
margen_izq = 0
margen_der = 0
margen_sup = 0
margen_inf = 0

pos_filtrados = [d for d in combo_filtrados 
                 if (shooting_zone[2] + margen_izq <= d['pos'][1] <= shooting_zone[3] - margen_der) and
                    (shooting_zone[0] + margen_sup <= d['pos'][0] <= shooting_zone[1] - margen_inf)]

print(f"   Excluir bordes: izq={margen_izq}px, der={margen_der}px, sup={margen_sup}px, inf={margen_inf}px")
print(f"   ❌ Elimina (área + ratio + posición): {len(falsos) - len(pos_filtrados)}/{len(falsos)} falsos positivos")
print(f"   ⚠️ Quedan: {len(pos_filtrados)} falsos positivos")

# Verificar que dinos reales pasan todos los filtros
dinos_sobreviven = [d for d in dinos 
                    if (filtro_min_area <= d['area'] <= filtro_max_area) and
                       (filtro_min_ratio <= d['aspect_ratio'] <= filtro_max_ratio) and
                       (shooting_zone[2] + margen_izq <= d['pos'][1] <= shooting_zone[3] - margen_der) and
                       (shooting_zone[0] + margen_sup <= d['pos'][0] <= shooting_zone[1] - margen_inf)]
print(f"   ✅ Dinos que sobreviven todos los filtros: {len(dinos_sobreviven)}/{len(dinos)}")

# Resumen final
total_detectado = len(dinos) + len(pos_filtrados)
precision_original = len(dinos) / len(detecciones) * 100
precision_mejorada = len(dinos) / total_detectado * 100 if total_detectado > 0 else 0

print("\n" + "="*70)
print("📊 RESUMEN")
print("="*70)
print(f"Detecciones originales: {len(detecciones)}")
print(f"Detecciones después de filtros: {total_detectado}")
print(f"Reducción: {(1 - total_detectado/len(detecciones))*100:.1f}%")
print(f"Precisión original: {precision_original:.1f}%")
print(f"Precisión mejorada: {precision_mejorada:.1f}%")
print(f"Mejora: {precision_mejorada - precision_original:.1f} puntos porcentuales")

# Visualizar detecciones filtradas
print("\n🎨 Generando visualización...")
fig, axes = plt.subplots(1, 2, figsize=(18, 8))

# Imagen 1: Detecciones originales (solo top 30)
ax = axes[0]
ax.imshow(background_cropped)
ax.set_title(f'SOBEL ORIGINAL\n{len(detecciones)} detecciones (mostrando top 30)', 
             fontsize=14, fontweight='bold')

for i, d in enumerate(detecciones[:30], 1):
    row = d['pos'][0] - shooting_zone[0]
    col = d['pos'][1] - shooting_zone[2]
    
    if d['es_dino_real']:
        color = 'lime'
        linewidth = 3
    else:
        color = 'red'
        linewidth = 1
    
    circle = plt.Circle((col, row), 15, color=color, fill=False, linewidth=linewidth)
    ax.add_patch(circle)
    ax.text(col, row, str(i), color='white', fontsize=9, ha='center', va='center',
            bbox=dict(boxstyle='circle', facecolor=color, alpha=0.7))

# Leyenda
real_patch = mpatches.Patch(color='lime', label=f'Dinos reales ({len(dinos)})')
false_patch = mpatches.Patch(color='red', label=f'Falsos positivos ({len(falsos)})')
ax.legend(handles=[real_patch, false_patch], loc='upper right', fontsize=10)
ax.axis('off')

# Imagen 2: Detecciones filtradas
ax = axes[1]
ax.imshow(background_cropped)
ax.set_title(f'SOBEL + FILTROS\n{total_detectado} detecciones', 
             fontsize=14, fontweight='bold')

# Dibujar dinos reales que sobreviven
for i, d in enumerate(dinos_sobreviven, 1):
    row = d['pos'][0] - shooting_zone[0]
    col = d['pos'][1] - shooting_zone[2]
    
    circle = plt.Circle((col, row), 15, color='lime', fill=False, linewidth=3)
    ax.add_patch(circle)
    ax.text(col, row, str(i), color='white', fontsize=9, ha='center', va='center',
            bbox=dict(boxstyle='circle', facecolor='lime', alpha=0.7))

# Dibujar falsos positivos que quedan
for i, d in enumerate(pos_filtrados, len(dinos_sobreviven) + 1):
    row = d['pos'][0] - shooting_zone[0]
    col = d['pos'][1] - shooting_zone[2]
    
    circle = plt.Circle((col, row), 15, color='orange', fill=False, linewidth=1)
    ax.add_patch(circle)
    ax.text(col, row, str(i), color='white', fontsize=9, ha='center', va='center',
            bbox=dict(boxstyle='circle', facecolor='orange', alpha=0.7))

# Leyenda
real_patch = mpatches.Patch(color='lime', label=f'Dinos reales ({len(dinos_sobreviven)})')
remain_patch = mpatches.Patch(color='orange', label=f'Falsos positivos ({len(pos_filtrados)})')
ax.legend(handles=[real_patch, remain_patch], loc='upper right', fontsize=10)
ax.axis('off')

# Agregar texto con filtros aplicados
filtros_text = f"""FILTROS APLICADOS:
• Área: {filtro_min_area}-{filtro_max_area}px
• Aspect ratio: {filtro_min_ratio:.2f}-{filtro_max_ratio:.2f}
• Bordes excluidos: {margen_izq}/{margen_der}/{margen_sup}/{margen_inf}px

MEJORA: {precision_original:.1f}% → {precision_mejorada:.1f}%
REDUCCIÓN: {len(detecciones)} → {total_detectado} detecciones"""

fig.text(0.5, 0.02, filtros_text, ha='center', fontsize=10, 
         bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.tight_layout()
output_path = 'debug_screenshots/map_initial_20260131_164303_DINOS_OPTIMIZED.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight')
print(f"✅ Guardado: {output_path}")

# Imprimir código para implementar
print("\n" + "="*70)
print("💻 CÓDIGO PARA IMPLEMENTAR EN jw_bot.py")
print("="*70)
print(f"""
# En detect_dino(), después de obtener regions:
MIN_AREA = {filtro_min_area}
MAX_AREA = {filtro_max_area}
MIN_RATIO = {filtro_min_ratio:.2f}
MAX_RATIO = {filtro_max_ratio:.2f}
MARGEN_IZQ = {margen_izq}
MARGEN_DER = {margen_der}
MARGEN_SUP = {margen_sup}
MARGEN_INF = {margen_inf}

for region in regions:
    # Calcular características
    area = region.area
    bbox = region.bbox
    height = bbox[2] - bbox[0]
    width = bbox[3] - bbox[1]
    aspect_ratio = width / height if height > 0 else 0
    
    # Aplicar filtros
    if not (MIN_AREA <= area <= MAX_AREA):
        continue  # Área fuera de rango
    if not (MIN_RATIO <= aspect_ratio <= MAX_RATIO):
        continue  # Forma incorrecta
    
    # Calcular posición
    label_dist = dist * (labels == region.label).astype(np.uint8)
    row, col = np.unravel_index(label_dist.argmax(), label_dist.shape)
    
    # Filtrar bordes
    if col < MARGEN_IZQ or col > (self.shooting_zone[3] - self.shooting_zone[2] - MARGEN_DER):
        continue
    if row < MARGEN_SUP or row > (self.shooting_zone[1] - self.shooting_zone[0] - MARGEN_INF):
        continue
    
    # Guardar detección válida
    pos.append([self.shooting_zone[0] + row, self.shooting_zone[2] + col])
""")

print("\n✅ ¡Análisis completo!")
