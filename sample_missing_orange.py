"""
Samplear naranja faltante entre verdes 1-2 y arriba del naranja 3
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def sample_missing_orange(image_path, position, radius=3):
    """Samplea RGB del naranja faltante"""
    
    print("="*80)
    print(f"🟠 SAMPLEANDO NARANJA FALTANTE")
    print("="*80)
    print(f"📍 Posición estimada: {position}")
    print(f"📏 Radio: {radius} píxeles\n")
    
    # Cargar imagen
    img = plt.imread(image_path)
    
    # Convertir a RGB 0-255
    if img.max() <= 1.0:
        img_rgb = (img * 255).astype(np.uint8)
    else:
        img_rgb = img.astype(np.uint8)
    
    y, x = position
    
    # Samplear área circular
    samples = []
    for dy in range(-radius, radius+1):
        for dx in range(-radius, radius+1):
            if dy*dy + dx*dx <= radius*radius:
                py = y + dy
                px = x + dx
                if 0 <= py < img_rgb.shape[0] and 0 <= px < img_rgb.shape[1]:
                    samples.append(img_rgb[py, px, :3])
    
    samples = np.array(samples)
    
    print(f"✅ Sampleados {len(samples)} píxeles\n")
    
    # Estadísticas
    print("📊 ESTADÍSTICAS RGB (0-255):")
    print("-" * 80)
    print(f"{'Canal':<8} {'Min':>6} {'Max':>6} {'Media':>8} {'Mediana':>8} {'Std':>8}")
    print("-" * 80)
    
    for i, color in enumerate(['R', 'G', 'B']):
        channel = samples[:, i]
        print(f"{color:<8} {channel.min():>6.0f} {channel.max():>6.0f} {channel.mean():>8.1f} {np.median(channel):>8.0f} {channel.std():>8.1f}")
    
    print("-" * 80)
    
    # Comparar con rangos actuales
    print("\n🔄 COMPARACIÓN:")
    print("-" * 80)
    print(f"Naranja actual:   R[235-255] G[120-165] B[10-30]")
    print(f"Naranja detectado: R[255]     G[143]     B[18]")
    print(f"Este naranja:     R[{samples[:,0].min():.0f}-{samples[:,0].max():.0f}] G[{samples[:,1].min():.0f}-{samples[:,1].max():.0f}] B[{samples[:,2].min():.0f}-{samples[:,2].max():.0f}]")
    print("-" * 80)
    
    # Visualización
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # Mapa completo
    axes[0].imshow(img)
    circle = patches.Circle((x, y), radius, linewidth=3, 
                           edgecolor='orange', facecolor='none')
    axes[0].add_patch(circle)
    axes[0].plot(x, y, 'r+', markersize=20, markeredgewidth=3)
    
    # Marcar referencias
    axes[0].plot(259, 233, 'go', markersize=10, label='Verde 2')
    axes[0].plot(314, 266, 'o', color='orange', markersize=10, label='Naranja 3')
    axes[0].set_title(f'Naranja Faltante - [{y}, {x}]', fontsize=14)
    axes[0].legend()
    axes[0].axis('off')
    
    # Zoom
    margin = 80
    y_min = max(0, y - margin)
    y_max = min(img.shape[0], y + margin)
    x_min = max(0, x - margin)
    x_max = min(img.shape[1], x + margin)
    
    axes[1].imshow(img[y_min:y_max, x_min:x_max])
    axes[1].plot(x - x_min, y - y_min, 'r+', markersize=20, markeredgewidth=3)
    axes[1].set_title(f'Zoom - Radio {radius}px', fontsize=14)
    axes[1].axis('off')
    
    # Histograma
    axes[2].hist(samples[:, 0], bins=30, alpha=0.5, color='red', label='R')
    axes[2].hist(samples[:, 1], bins=30, alpha=0.5, color='green', label='G')
    axes[2].hist(samples[:, 2], bins=30, alpha=0.5, color='blue', label='B')
    axes[2].axvline(samples[:, 0].mean(), color='red', linestyle='--', linewidth=2)
    axes[2].axvline(samples[:, 1].mean(), color='green', linestyle='--', linewidth=2)
    axes[2].axvline(samples[:, 2].mean(), color='blue', linestyle='--', linewidth=2)
    axes[2].set_title('Distribución RGB', fontsize=14)
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_path = image_path.replace('.png', '_MISSING_ORANGE.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\n✅ Visualización guardada: {output_path}")
    print("="*80)

if __name__ == "__main__":
    image_path = "debug_screenshots/map_initial_20260131_164303.png"
    
    # Posición estimada del naranja faltante
    # Descripción: arriba del naranja 3 [266, 314], cerca del verde 2 [233, 259]
    # Estimación: Y entre 200-230, X cercano a 300-315
    
    print("🔍 BUSCANDO NARANJA FALTANTE:")
    print("   Verde 2: [233, 259]")
    print("   Naranja 3: [266, 314]")
    print("   Ubicación: arriba del 3, cerca del verde 2, casi en línea recta\n")
    
    # Ajuste fino: más arriba y medio pixel a la izquierda desde [205, 305]
    # Usuario dice: más arriba y medio pixel a la izquierda
    for y_offset, x_offset in [(-5, -1), (-6, -1), (-7, -1), (-8, -1)]:
        position = [205 + y_offset, 305 + x_offset]
        print(f"\n{'='*80}")
        print(f"Probando posición: {position} (offset Y:{y_offset} X:{x_offset})")
        print('='*80)
        sample_missing_orange(image_path, position, radius=3)
