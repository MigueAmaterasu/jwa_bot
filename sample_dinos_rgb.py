"""
Samplear color RGB de los 4 dinosaurios reales
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def sample_dino_rgb(image_path, position, dino_id, radius=5):
    """Samplea RGB de un dino"""
    
    print("="*80)
    print(f"🦖 SAMPLEANDO DINO #{dino_id}")
    print("="*80)
    print(f"📍 Posición: {position}")
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
    print(f"{'Canal':<8} {'Min':>6} {'Max':>6} {'Media':>8} {'Mediana':>8}")
    print("-" * 80)
    
    for i, color in enumerate(['R', 'G', 'B']):
        channel = samples[:, i]
        print(f"{color:<8} {channel.min():>6.0f} {channel.max():>6.0f} {channel.mean():>8.1f} {np.median(channel):>8.0f}")
    
    print("-" * 80)
    
    return samples

def visualize_all_dinos(image_path, dino_positions, all_samples):
    """Visualiza todos los dinos y sus colores"""
    
    img = plt.imread(image_path)
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # Mapa con dinos marcados
    axes[0, 0].imshow(img)
    axes[0, 0].set_title('4 Dinosaurios Reales', fontsize=14, weight='bold')
    
    colors_display = ['red', 'blue', 'green', 'orange']
    for i, (dino_id, pos) in enumerate(dino_positions.items()):
        y, x = pos
        circle = patches.Circle((x, y), radius=20, linewidth=3, 
                               edgecolor=colors_display[i], facecolor='none')
        axes[0, 0].add_patch(circle)
        axes[0, 0].text(x-15, y-25, f"#{dino_id}", fontsize=12, 
                       color=colors_display[i], weight='bold',
                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    axes[0, 0].axis('off')
    
    # Zooms individuales de cada dino
    for idx, (dino_id, pos) in enumerate(dino_positions.items()):
        row = (idx + 1) // 3
        col = (idx + 1) % 3
        
        y, x = pos
        margin = 40
        y_min = max(0, y - margin)
        y_max = min(img.shape[0], y + margin)
        x_min = max(0, x - margin)
        x_max = min(img.shape[1], x + margin)
        
        axes[row, col].imshow(img[y_min:y_max, x_min:x_max])
        axes[row, col].plot(x - x_min, y - y_min, '+', color=colors_display[idx],
                           markersize=20, markeredgewidth=3)
        axes[row, col].set_title(f'Dino #{dino_id} - [{y}, {x}]', fontsize=12)
        axes[row, col].axis('off')
    
    # Histograma combinado
    axes[1, 2].set_title('RGB de todos los dinos', fontsize=12)
    
    for idx, (dino_id, samples) in enumerate(all_samples.items()):
        alpha = 0.3
        axes[1, 2].hist(samples[:, 0], bins=30, alpha=alpha, color='red', 
                       label=f'R #{dino_id}' if idx == 0 else '')
        axes[1, 2].hist(samples[:, 1], bins=30, alpha=alpha, color='green',
                       label=f'G #{dino_id}' if idx == 0 else '')
        axes[1, 2].hist(samples[:, 2], bins=30, alpha=alpha, color='blue',
                       label=f'B #{dino_id}' if idx == 0 else '')
    
    axes[1, 2].set_xlabel('Valor (0-255)')
    axes[1, 2].set_ylabel('Frecuencia')
    axes[1, 2].legend()
    axes[1, 2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_path = image_path.replace('.png', '_DINOS_RGB_ANALYSIS.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\n✅ Visualización guardada: {output_path}")

if __name__ == "__main__":
    image_path = "debug_screenshots/map_initial_20260131_164303.png"
    
    # 4 dinos reales confirmados por el usuario
    dino_positions = {
        2: [509, 329],   # Grande
        12: [480, 10],   # Mediano
        26: [367, 261],  # Pequeño
        27: [447, 225],  # Pequeño
    }
    
    print("🦖 ANÁLISIS RGB DE DINOSAURIOS REALES")
    print("="*80)
    print(f"Total dinos a analizar: {len(dino_positions)}\n")
    
    all_samples = {}
    
    for dino_id, pos in dino_positions.items():
        samples = sample_dino_rgb(image_path, pos, dino_id, radius=5)
        all_samples[dino_id] = samples
        print()
    
    # Calcular rangos combinados
    print("\n" + "="*80)
    print("📊 RANGOS COMBINADOS DE TODOS LOS DINOS:")
    print("="*80)
    
    all_r = np.concatenate([s[:, 0] for s in all_samples.values()])
    all_g = np.concatenate([s[:, 1] for s in all_samples.values()])
    all_b = np.concatenate([s[:, 2] for s in all_samples.values()])
    
    print(f"\nR: min={all_r.min():.0f} max={all_r.max():.0f} media={all_r.mean():.1f}")
    print(f"G: min={all_g.min():.0f} max={all_g.max():.0f} media={all_g.mean():.1f}")
    print(f"B: min={all_b.min():.0f} max={all_b.max():.0f} media={all_b.mean():.1f}")
    
    # Rangos recomendados con margen
    r_min = max(0, int(all_r.min() - 10))
    r_max = min(255, int(all_r.max() + 10))
    g_min = max(0, int(all_g.min() - 10))
    g_max = min(255, int(all_g.max() + 10))
    b_min = max(0, int(all_b.min() - 10))
    b_max = min(255, int(all_b.max() + 10))
    
    print(f"\n💡 RANGOS RECOMENDADOS (con margen ±10):")
    print("-" * 80)
    print(f"R: [{r_min}, {r_max}]")
    print(f"G: [{g_min}, {g_max}]")
    print(f"B: [{b_min}, {b_max}]")
    print("="*80)
    
    # Visualizar
    visualize_all_dinos(image_path, dino_positions, all_samples)
    
    print("\n🔍 SIGUIENTE PASO:")
    print("   1. Revisar imagen: map_initial_20260131_164303_DINOS_RGB_ANALYSIS.png")
    print("   2. Verificar que los 4 cruces estén en los dinos correctos")
    print("   3. Probar detección con nuevos rangos RGB")
    print("="*80)
