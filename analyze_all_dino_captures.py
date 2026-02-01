#!/usr/bin/env python3
"""
Analiza TODAS las capturas de dinos para identificar patrones de falsos positivos
"""

import os
import glob
from skimage import io
import matplotlib.pyplot as plt

# Encontrar todas las imágenes de dinos
dino_images = sorted(glob.glob('debug_screenshots/dinos/dino_*.png'))

print("="*70)
print(f"📊 ANÁLISIS DE {len(dino_images)} CAPTURAS DE DINOS")
print("="*70)

for img_path in dino_images:
    filename = os.path.basename(img_path)
    # Extraer número de detecciones del nombre: dino_timestamp_contador_nXX.png
    parts = filename.replace('.png', '').split('_')
    n_detections = int(parts[-1].replace('n', ''))
    
    print(f"\n📸 {filename}")
    print(f"   Detecciones: {n_detections}")
    print(f"   Por favor revisar y reportar:")
    print(f"   ✅ Dinos reales: #X, #Y, #Z")
    print(f"   ❌ Falsos positivos: resto")

print("\n" + "="*70)
print("🔍 INSTRUCCIONES:")
print("="*70)
print("1. Abre cada imagen con: open debug_screenshots/dinos/")
print("2. Anota para CADA imagen:")
print("   - Números de círculos que son DINOS REALES")
print("   - Qué son los falsos positivos (árboles, edificios, etc.)")
print("\n3. Formato de reporte:")
print("   dino_XXX_n16.png → Reales: #1, #4 | Falsos: #2-3,#5-16 (edificios/árboles)")
print("\n4. Con esos datos ajustaremos los filtros")
print("="*70)
