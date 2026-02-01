#!/usr/bin/env python3
"""
Toma captura ACTUAL y analiza colores RGB de supplies visibles
para comparar con los rangos configurados
"""

import pyautogui
import numpy as np
from PIL import Image
import time

print("="*70)
print("📸 ANÁLISIS RGB EN TIEMPO REAL")
print("="*70)
print("\nINSTRUCCIONES:")
print("1. Asegúrate de que BlueStacks esté visible con supplies en pantalla")
print("2. Tienes 5 segundos para posicionarte...")

for i in range(5, 0, -1):
    print(f"   {i}...")
    time.sleep(1)

print("\n📸 Tomando captura...")

# Tomar captura de pantalla completa
screenshot = pyautogui.screenshot()
screenshot.save('debug_screenshots/live_capture.png')
print(f"✅ Guardada: debug_screenshots/live_capture.png")

# Convertir a numpy array
img = np.array(screenshot)

print("\n" + "="*70)
print("🎨 RANGOS RGB CONFIGURADOS ACTUALMENTE:")
print("="*70)
print("EVENTO VERDE:")
print("  R: [10-40]   G: [200-235]   B: [5-30]")
print("  Ejemplo real anterior: RGB(22, 219, 13)")
print("\nSUPPLY NARANJA:")
print("  R: [233-255]   G: [120-165]   B: [0-30]")
print("  Ejemplo real anterior: RGB(255, 143, 18)")

print("\n" + "="*70)
print("📍 SIGUIENTE PASO:")
print("="*70)
print("1. Abre la imagen: open debug_screenshots/live_capture.png")
print("2. Identifica un supply drop naranja visible")
print("3. Anota las coordenadas X, Y del centro del supply")
print("4. Ejecuta: .venv/bin/python sample_live_supply.py X Y")
print("   (sustituye X Y con las coordenadas)")
print("\nEsto nos dirá el RGB REAL que tiene ahora vs lo configurado")
print("="*70)
