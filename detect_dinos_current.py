"""
Detectar dinosaurios con el método actual del bot (Sobel edge detection)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from skimage import filters, morphology, measure
from scipy import ndimage

def detect_dinos_current_method(image_path):
    """Detecta dinos con el método actual del bot (Sobel)"""
    
    print("="*80)
    print("🦖 DETECTANDO DINOSAURIOS (método actual: Sobel edge detection)")
    print("="*80)
    
    # Cargar imagen
    img = plt.imread(image_path)
    
    # Zona de disparo (igual que el bot)
    shooting_zone = (230, 720, 10, 440)
    
    # Recortar zona
    background_cropped = img[shooting_zone[0]:shooting_zone[1],
                            shooting_zone[2]:shooting_zone[3]]
    
    print(f"\n📐 Zona de disparo: Y[{shooting_zone[0]}-{shooting_zone[1]}] X[{shooting_zone[2]}-{shooting_zone[3]}]")
    
    # Detección de bordes (Sobel)
    edges = filters.sobel(background_cropped)
    
    # Máscara: bordes bajos (áreas uniformes = posibles dinos)
    mask = ((edges[:,:,0] <= 0.089) & 
            (edges[:,:,1] <= 0.089) & 
            (edges[:,:,2] <= 0.089))
    
    # Filtros
    mask = filters.median(mask, np.ones((3, 3)))
    mask = morphology.binary_closing(mask, np.ones((5, 5)))
    
    # Componentes conectados
    labels = measure.label(mask, background=0, connectivity=2)
    dist = ndimage.distance_transform_edt(mask)
    
    print(f"🔢 Componentes detectados: {labels.max()}")
    
    # Encontrar centro de masa de cada componente
    detections = []
    for label in range(1, labels.max()+1):
        label_dist = dist * (labels == label).astype(np.uint8)
        row, col = np.unravel_index(label_dist.argmax(), label_dist.shape)
        
        # Convertir a coordenadas globales
        global_y = shooting_zone[0] + row
        global_x = shooting_zone[2] + col
        
        # Contar píxeles del componente
        component_pixels = np.sum(labels == label)
        
        detections.append({
            'pos': [global_y, global_x],
            'pixels': component_pixels,
            'label': label
        })
    
    # Ordenar por tamaño
    detections.sort(key=lambda d: d['pixels'], reverse=True)
    
    print(f"\n✅ DETECTADOS: {len(detections)} posibles dinosaurios\n")
    
    if len(detections) > 0:
        print("📋 LISTA DE DETECCIONES (ordenadas por tamaño):")
        print("-" * 80)
        print(f"{'#':<4} {'Posición [Y, X]':<20} {'Tamaño (px)':<15}")
        print("-" * 80)
        
        for i, det in enumerate(detections[:20], 1):  # Top 20
            print(f"{i:<4} {str(det['pos']):<20} {det['pixels']:<15}")
        
        if len(detections) > 20:
            print(f"... y {len(detections) - 20} más")
        
        print("-" * 80)
    
    # Crear visualización
    fig, axes = plt.subplots(2, 2, figsize=(16, 20))
    
    # 1. Mapa completo con detecciones
    axes[0, 0].imshow(img)
    axes[0, 0].set_title(f'Dinosaurios Detectados: {len(detections)}', fontsize=14)
    
    for i, det in enumerate(detections[:30], 1):  # Top 30
        y, x = det['pos']
        pixels = det['pixels']
        
        # Círculo rojo
        circle = patches.Circle((x, y), radius=15, linewidth=2, 
                               edgecolor='red', facecolor='none')
        axes[0, 0].add_patch(circle)
        
        # Etiqueta
        axes[0, 0].text(x-10, y-20, f"{i}\n{pixels}px", fontsize=8, color='red',
                       weight='bold',
                       bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
    
    # Marcar zona de disparo
    rect = patches.Rectangle((shooting_zone[2], shooting_zone[0]), 
                             shooting_zone[3] - shooting_zone[2],
                             shooting_zone[1] - shooting_zone[0],
                             linewidth=3, edgecolor='cyan', facecolor='none',
                             linestyle='--')
    axes[0, 0].add_patch(rect)
    axes[0, 0].axis('off')
    
    # 2. Bordes (Sobel)
    axes[0, 1].imshow(edges)
    axes[0, 1].set_title('Detección de Bordes (Sobel)', fontsize=14)
    axes[0, 1].axis('off')
    
    # 3. Máscara
    axes[1, 0].imshow(mask, cmap='gray')
    axes[1, 0].set_title('Máscara (bordes bajos = dinos)', fontsize=14)
    axes[1, 0].axis('off')
    
    # 4. Labels
    axes[1, 1].imshow(labels, cmap='nipy_spectral')
    axes[1, 1].set_title(f'Componentes Conectados ({labels.max()})', fontsize=14)
    axes[1, 1].axis('off')
    
    plt.tight_layout()
    output_path = image_path.replace('.png', '_DINOS_CURRENT.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\n✅ Imagen guardada: {output_path}")
    print("="*80)
    
    return detections

if __name__ == "__main__":
    image_path = "debug_screenshots/map_initial_20260131_164303.png"
    
    detections = detect_dinos_current_method(image_path)
    
    print("\n🔍 POR FAVOR REVISAR:")
    print("   - Abre: debug_screenshots/map_initial_20260131_164303_DINOS_CURRENT.png")
    print("   - Panel superior izq: Mapa con círculos rojos en detecciones")
    print("   - Dime cuáles círculos están en dinosaurios REALES")
    print("   - El método actual usa detección de bordes, NO color")
    print("="*80)
