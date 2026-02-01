#!/usr/bin/env python3
"""
Analiza map_initial para ver por qué NO detecta supplies
Compara colores reales vs rangos configurados
"""

import numpy as np
from skimage import io, morphology, measure

# Cargar imagen
print("📸 Cargando map_initial_20260131_183307.png...")
img = io.imread('debug_screenshots/map_initial_20260131_183307.png')

# Zona de disparo (misma que el bot)
shooting_zone = [230, 720, 10, 440]
img_cropped = img[shooting_zone[0]:shooting_zone[1], shooting_zone[2]:shooting_zone[3]]

print(f"📐 Zona de disparo: Y[{shooting_zone[0]}-{shooting_zone[1]}] X[{shooting_zone[2]}-{shooting_zone[3]}]")
print(f"   Tamaño: {img_cropped.shape}")

# Rangos actuales configurados
print("\n" + "="*70)
print("🎨 RANGOS RGB CONFIGURADOS:")
print("="*70)

# Evento verde
green_ranges = {
    'R': (10, 40),
    'G': (200, 235),
    'B': (5, 30)
}
print(f"EVENTO VERDE: R{green_ranges['R']} G{green_ranges['G']} B{green_ranges['B']}")

# Supply naranja
orange_ranges = {
    'R': (233, 255),
    'G': (120, 165),
    'B': (0, 30)
}
print(f"SUPPLY NARANJA: R{orange_ranges['R']} G{orange_ranges['G']} B{orange_ranges['B']}")

# Detectar con rangos VERDES
print("\n" + "="*70)
print("🟢 PROBANDO DETECCIÓN CON RANGOS VERDES...")
print("="*70)

mask_green = ((img_cropped[:,:,0] >= green_ranges['R'][0]) & 
              (img_cropped[:,:,0] <= green_ranges['R'][1]) &
              (img_cropped[:,:,1] >= green_ranges['G'][0]) & 
              (img_cropped[:,:,1] <= green_ranges['G'][1]) &
              (img_cropped[:,:,2] >= green_ranges['B'][0]) & 
              (img_cropped[:,:,2] <= green_ranges['B'][1]))

mask_green = morphology.binary_opening(mask_green, np.ones((3,3)))
mask_green = morphology.binary_closing(mask_green, np.ones((5,5)))
labels_green = measure.label(mask_green, background=0, connectivity=2)

detections_green = []
for label in range(1, labels_green.max()+1):
    rows, cols = np.where(labels_green == label)
    if len(rows) > 70:  # min_pixels
        detections_green.append(len(rows))

print(f"✅ Detectados: {len(detections_green)} eventos verdes")
if detections_green:
    print(f"   Tamaños: {detections_green}")

# Detectar con rangos NARANJAS
print("\n" + "="*70)
print("🟠 PROBANDO DETECCIÓN CON RANGOS NARANJAS...")
print("="*70)

mask_orange = ((img_cropped[:,:,0] >= orange_ranges['R'][0]) & 
               (img_cropped[:,:,0] <= orange_ranges['R'][1]) &
               (img_cropped[:,:,1] >= orange_ranges['G'][0]) & 
               (img_cropped[:,:,1] <= orange_ranges['G'][1]) &
               (img_cropped[:,:,2] >= orange_ranges['B'][0]) & 
               (img_cropped[:,:,2] <= orange_ranges['B'][1]))

mask_orange = morphology.binary_opening(mask_orange, np.ones((3,3)))
mask_orange = morphology.binary_closing(mask_orange, np.ones((5,5)))
labels_orange = measure.label(mask_orange, background=0, connectivity=2)

detections_orange = []
for label in range(1, labels_orange.max()+1):
    rows, cols = np.where(labels_orange == label)
    if len(rows) > 70:  # min_pixels
        detections_orange.append(len(rows))

print(f"✅ Detectados: {len(detections_orange)} supplies naranjas")
if detections_orange:
    print(f"   Tamaños: {detections_orange}")

print("\n" + "="*70)
print("📊 RESUMEN:")
print("="*70)
print(f"Total detectado: {len(detections_green) + len(detections_orange)} supplies")
print(f"  🟢 Verdes: {len(detections_green)}")
print(f"  🟠 Naranjas: {len(detections_orange)}")
print(f"\n⚠️  Deberían ser ~11 supplies visibles en el mapa")

if len(detections_green) + len(detections_orange) == 0:
    print("\n" + "="*70)
    print("❌ PROBLEMA ENCONTRADO: ¡NO DETECTA NINGUNO!")
    print("="*70)
    print("Posibles causas:")
    print("1. Los rangos RGB son muy estrictos")
    print("2. La imagen tiene diferente brillo/saturación")
    print("3. Los supplies tienen colores ligeramente diferentes")
    print("\nSolución: Necesitamos samplear RGB de esta imagen específica")
    print("Ejecuta: open debug_screenshots/map_initial_20260131_183307.png")
    print("Y anota coordenadas de un supply naranja visible")
