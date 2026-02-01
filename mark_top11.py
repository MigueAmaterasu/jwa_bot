"""
Script para marcar los Top 11 objetos más grandes encontrados
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from skimage import measure, morphology

# Top 11 objetos más grandes encontrados
top_supplies = [
    {'pos': [490, 229], 'area': 128997, 'label': '1'},
    {'pos': [926, 446], 'area': 14602, 'label': '2'},
    {'pos': [32, 283], 'area': 3792, 'label': '3'},
    {'pos': [32, 425], 'area': 3430, 'label': '4'},
    {'pos': [32, 155], 'area': 3160, 'label': '5'},
    {'pos': [116, 46], 'area': 2443, 'label': '6'},
    {'pos': [963, 178], 'area': 1893, 'label': '7'},
    {'pos': [854, 286], 'area': 1579, 'label': '8'},
    {'pos': [816, 527], 'area': 1544, 'label': '9'},
    {'pos': [36, 524], 'area': 1481, 'label': '10'},
    {'pos': [424, 526], 'area': 1382, 'label': '11'},
]

def mark_top_supplies(image_path):
    """Marca los Top 11 objetos más grandes"""
    
    print("="*80)
    print("📍 MARCANDO TOP 11 OBJETOS MÁS GRANDES")
    print("="*80)
    print(f"📁 Imagen: {image_path}")
    print(f"📊 Total: {len(top_supplies)} objetos\n")
    
    # Cargar imagen
    img = plt.imread(image_path)
    
    # Crear figura
    fig, ax = plt.subplots(1, 1, figsize=(12, 20))
    ax.imshow(img)
    ax.set_title('Top 11 Objetos Más Grandes (>=200 píxeles)', fontsize=16)
    
    # Marcar cada posición
    for supply in top_supplies:
        y, x = supply['pos']
        area = supply['area']
        label = supply['label']
        
        # Círculo azul (diferente del rojo anterior)
        circle = patches.Circle((x, y), radius=25, linewidth=4, 
                               edgecolor='blue', facecolor='none')
        ax.add_patch(circle)
        
        # Etiqueta con área
        text = f"{label}\n{area:.0f}px"
        ax.text(x-20, y-35, text, fontsize=14, color='blue',
               weight='bold',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        print(f"   {label:2s}. Pos {supply['pos']} - {area:>6.0f} píxeles")
    
    # Guardar
    output_path = image_path.replace('.png', '_TOP11.png')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\n✅ Imagen guardada: {output_path}")
    print("="*80)
    print("\n🔍 POR FAVOR REVISAR:")
    print("   - Cuáles de estos 11 SON supplies reales (naranjas o verdes)?")
    print("   - El #1 tiene 128,997 píxeles (ENORME) - podría ser background/mapa")
    print("   - Los #2-11 son más pequeños (1,382 - 14,602 píxeles)")
    print("   - Deberían haber 11 supplies reales según tu conteo manual")
    print("="*80)

if __name__ == "__main__":
    image_path = "debug_screenshots/map_initial_20260131_164303.png"
    mark_top_supplies(image_path)
