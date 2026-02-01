"""
Script para detectar los 3 EVENTOS ESPECIALES (verdes)
Usando los valores RGB REALES del #10: RGB(22, 219, 13)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from skimage import measure, morphology

def detect_green_events(image_path):
    """Detecta eventos especiales verdes con rangos RGB reales"""
    
    print("="*80)
    print("🔍 DETECTANDO EVENTOS ESPECIALES (VERDES)")
    print("="*80)
    print("Rangos basados en supply #10 [419, 331]:")
    print("  RGB real: (22, 219, 13)")
    print("  Rangos con tolerancia:")
    print("    R: [10-40]   (rojo MUY bajo)")
    print("    G: [200-235] (verde MUY alto)")
    print("    B: [5-30]    (azul MUY bajo)")
    print("="*80 + "\n")
    
    # Cargar imagen
    img = plt.imread(image_path)
    
    # Convertir a RGB 0-255
    if img.max() <= 1.0:
        img_rgb = (img * 255).astype(np.uint8)
    else:
        img_rgb = img.astype(np.uint8)
    
    # Máscara con rangos REALES del evento verde
    mask = (
        (img_rgb[:,:,0] >= 10) & (img_rgb[:,:,0] <= 40) &    # R bajo
        (img_rgb[:,:,1] >= 200) & (img_rgb[:,:,1] <= 235) &  # G alto
        (img_rgb[:,:,2] >= 5) & (img_rgb[:,:,2] <= 30)       # B bajo
    )
    
    # Morphology para conectar píxeles cercanos
    mask = morphology.binary_closing(mask, np.ones((5,5)))
    
    # Etiquetar componentes conectados
    labels = measure.label(mask)
    regions = measure.regionprops(labels)
    
    # Filtrar por tamaño mínimo
    min_pixels = 50  # Más restrictivo que 15
    events = []
    
    for region in regions:
        if region.area >= min_pixels:
            y, x = region.centroid
            events.append({
                'pos': [int(y), int(x)],
                'area': region.area,
                'bbox': region.bbox
            })
    
    # Ordenar por tamaño
    events.sort(key=lambda e: e['area'], reverse=True)
    
    print(f"✅ ENCONTRADOS: {len(events)} eventos especiales\n")
    
    if len(events) > 0:
        print("📋 LISTA DE EVENTOS DETECTADOS:")
        print("-" * 80)
        print(f"{'#':<4} {'Posición [Y, X]':<20} {'Tamaño (px)':<15} {'Bbox'}")
        print("-" * 80)
        
        for i, event in enumerate(events, 1):
            print(f"{i:<4} {str(event['pos']):<20} {event['area']:<15} {event['bbox']}")
        
        print("-" * 80)
    
    # Verificar si el #10 original está en la lista
    original_pos = [419, 331]
    found_original = False
    for i, event in enumerate(events, 1):
        dist = ((event['pos'][0] - original_pos[0])**2 + 
                (event['pos'][1] - original_pos[1])**2)**0.5
        if dist < 20:  # Dentro de 20px
            print(f"\n✅ Supply #10 original ENCONTRADO como #{i}")
            print(f"   Posición original: {original_pos}")
            print(f"   Posición detectada: {event['pos']}")
            print(f"   Distancia: {dist:.1f} px")
            found_original = True
            break
    
    if not found_original:
        print(f"\n❌ Supply #10 original NO encontrado en las detecciones")
        print(f"   Posición esperada: {original_pos}")
    
    # Crear visualización
    fig, ax = plt.subplots(1, 1, figsize=(12, 20))
    ax.imshow(img)
    ax.set_title(f'Eventos Especiales Detectados: {len(events)}', fontsize=16)
    
    # Marcar cada evento
    for i, event in enumerate(events, 1):
        y, x = event['pos']
        area = event['area']
        
        # Círculo verde
        circle = patches.Circle((x, y), radius=20, linewidth=3, 
                               edgecolor='lime', facecolor='none')
        ax.add_patch(circle)
        
        # Etiqueta
        text = f"{i}\n{area}px"
        ax.text(x-15, y-30, text, fontsize=12, color='lime',
               weight='bold',
               bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
    
    # Marcar posición original del #10 con cruz roja
    ax.plot(original_pos[1], original_pos[0], 'r+', 
            markersize=30, markeredgewidth=4, label='Supply #10 original')
    ax.legend(loc='upper right', fontsize=12)
    
    # Guardar
    output_path = image_path.replace('.png', '_GREEN_EVENTS.png')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\n✅ Imagen guardada: {output_path}")
    print("="*80)
    
    return events

if __name__ == "__main__":
    image_path = "debug_screenshots/map_initial_20260131_164303.png"
    events = detect_green_events(image_path)
    
    print("\n💡 RESULTADO ESPERADO:")
    print("   - Deberían detectarse 3 eventos especiales (verdes)")
    print("   - El supply #10 [419, 331] debería estar entre ellos")
    print("   - Si detecta más de 3, hay falsos positivos")
    print("   - Si detecta menos de 3, faltan eventos o rangos muy estrictos")
    print("="*80)
