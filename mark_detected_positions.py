"""
Script para marcar las posiciones detectadas en la imagen del mapa

Este script:
1. Lee la imagen del mapa inicial
2. Marca las 42 posiciones detectadas con círculos numerados
3. Guarda imagen nueva para que el usuario identifique cuáles son reales

Uso:
    python mark_detected_positions.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager
import sys

# Las 42 posiciones detectadas del log
detected_positions = [
    [328, 157], [286, 377], [281, 456], [349, 429], [290, 503],
    [293, 342], [304, 299], [302, 339], [313, 328], [419, 331],
    [479, 49], [444, 371], [524, 330], [457, 369], [462, 456],
    [468, 85], [519, 222], [520, 201], [528, 422], [542, 399],
    [566, 23], [576, 327], [630, 145], [618, 248], [627, 341],
    [632, 190], [638, 172], [648, 26], [660, 434], [684, 79],
    [702, 27], [684, 62], [690, 329], [693, 44], [706, 41],
    [714, 74], [717, 15], [736, 317], [754, 52], [764, 316],
    [762, 133], [766, 170]
]

def mark_positions(image_path):
    """Marca todas las posiciones detectadas en la imagen"""
    
    print("="*80)
    print("📍 MARCANDO POSICIONES DETECTADAS")
    print("="*80)
    print(f"\n📁 Imagen: {image_path}")
    print(f"📊 Total detectado: {len(detected_positions)} posiciones\n")
    
    # Cargar imagen
    try:
        img = plt.imread(image_path)
    except Exception as e:
        print(f"❌ Error al abrir imagen: {e}")
        return
    
    # Crear figura
    fig, ax = plt.subplots(1, 1, figsize=(12, 20))
    ax.imshow(img)
    
    # Marcar cada posición
    for idx, (y, x) in enumerate(detected_positions, 1):
        # Círculo rojo
        circle = patches.Circle((x, y), 15, linewidth=3, 
                               edgecolor='red', facecolor='none')
        ax.add_patch(circle)
        
        # Número con fondo blanco
        ax.text(x-10, y-25, str(idx), fontsize=16, color='red',
               bbox=dict(boxstyle='round', facecolor='white', 
                        edgecolor='red', linewidth=2))
    
    ax.axis('off')
    plt.tight_layout()
    
    # Guardar imagen marcada
    output_path = image_path.replace('.png', '_MARKED.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', pad_inches=0)
    plt.close()
    
    print(f"✅ Imagen guardada: {output_path}\n")
    
    # Mostrar lista de posiciones
    print("="*80)
    print("📋 LISTA DE POSICIONES (Y, X):")
    print("="*80)
    for idx, (y, x) in enumerate(detected_positions, 1):
        print(f"  {idx:2d}. [{y}, {x}]")
    
    print("\n" + "="*80)
    print("🎯 INSTRUCCIONES:")
    print("="*80)
    print(f"1. Abre la imagen: {output_path}")
    print("2. Verás 42 círculos rojos numerados del 1 al 42")
    print("3. Para cada número, identifica si es:")
    print("   ✅ SUPPLY REAL (naranja o verde)")
    print("   ❌ FALSO POSITIVO (árbol, edificio, UI, etc)")
    print("\n4. Dime solo los números que son REALES, ejemplo:")
    print("   'Reales: 1, 10, 14, 20, 33, 37, 40, 41, 42'")
    print("\n5. Con esa info ajustaremos los rangos de color correctamente!")
    print("="*80)

if __name__ == "__main__":
    image_path = "debug_screenshots/map_initial_20260131_164303.png"
    mark_positions(image_path)
