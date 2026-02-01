"""
Script para samplear el color RGB del supply #10 [419, 331]
Este es el ÚNICO supply válido confirmado por el usuario
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def sample_rgb_around_position(image_path, position, radius=30):
    """Samplea RGB en un área alrededor de la posición"""
    
    print("="*80)
    print(f"🎨 SAMPLEANDO RGB DEL SUPPLY #10 (ÚNICO VÁLIDO)")
    print("="*80)
    print(f"📍 Posición: {position}")
    print(f"📏 Radio de sampleo: {radius} píxeles\n")
    
    # Cargar imagen
    img = plt.imread(image_path)
    
    # Convertir a RGB 0-255
    if img.max() <= 1.0:
        img_rgb = (img * 255).astype(np.uint8)
    else:
        img_rgb = img.astype(np.uint8)
    
    y, x = position
    
    # Samplear área circular alrededor de la posición
    samples = []
    for dy in range(-radius, radius+1):
        for dx in range(-radius, radius+1):
            if dy*dy + dx*dx <= radius*radius:  # Dentro del círculo
                py = y + dy
                px = x + dx
                if 0 <= py < img_rgb.shape[0] and 0 <= px < img_rgb.shape[1]:
                    samples.append(img_rgb[py, px, :3])  # RGB
    
    samples = np.array(samples)
    
    print(f"✅ Sampleados {len(samples)} píxeles\n")
    
    # Análisis estadístico
    print("📊 ESTADÍSTICAS RGB (0-255):")
    print("-" * 80)
    print(f"{'Canal':<8} {'Min':>6} {'Max':>6} {'Media':>8} {'Mediana':>8} {'Std':>8}")
    print("-" * 80)
    
    for i, color in enumerate(['R', 'G', 'B']):
        channel = samples[:, i]
        print(f"{color:<8} {channel.min():>6.0f} {channel.max():>6.0f} {channel.mean():>8.1f} {np.median(channel):>8.0f} {channel.std():>8.1f}")
    
    print("-" * 80)
    
    # Rangos recomendados (mean ± 2*std)
    print("\n💡 RANGOS RECOMENDADOS (Mean ± 2×Std):")
    print("-" * 80)
    
    r_min = max(0, int(samples[:, 0].mean() - 2*samples[:, 0].std()))
    r_max = min(255, int(samples[:, 0].mean() + 2*samples[:, 0].std()))
    g_min = max(0, int(samples[:, 1].mean() - 2*samples[:, 1].std()))
    g_max = min(255, int(samples[:, 1].mean() + 2*samples[:, 1].std()))
    b_min = max(0, int(samples[:, 2].mean() - 2*samples[:, 2].std()))
    b_max = min(255, int(samples[:, 2].mean() + 2*samples[:, 2].std()))
    
    print(f"R: [{r_min}, {r_max}]")
    print(f"G: [{g_min}, {g_max}]")
    print(f"B: [{b_min}, {b_max}]")
    print("-" * 80)
    
    # Comparar con rangos actuales
    print("\n🔄 COMPARACIÓN CON RANGOS ACTUALES:")
    print("-" * 80)
    current_supply = "R[160-255] G[60-255] B[0-120]"
    print(f"Actual supply:    {current_supply}")
    print(f"Recomendado:      R[{r_min}-{r_max}] G[{g_min}-{g_max}] B[{b_min}-{b_max}]")
    print("-" * 80)
    
    # Crear visualización
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # 1. Imagen original con área marcada
    axes[0].imshow(img)
    circle = patches.Circle((x, y), radius, linewidth=3, 
                           edgecolor='red', facecolor='none')
    axes[0].add_patch(circle)
    axes[0].plot(x, y, 'r+', markersize=20, markeredgewidth=3)
    axes[0].set_title(f'Supply #10 - Posición [{y}, {x}]', fontsize=14)
    axes[0].axis('off')
    
    # 2. Zoom del área
    margin = 50
    y_min = max(0, y - margin)
    y_max = min(img.shape[0], y + margin)
    x_min = max(0, x - margin)
    x_max = min(img.shape[1], x + margin)
    
    axes[1].imshow(img[y_min:y_max, x_min:x_max])
    axes[1].plot(x - x_min, y - y_min, 'r+', markersize=20, markeredgewidth=3)
    axes[1].set_title(f'Zoom - Radio {radius}px', fontsize=14)
    axes[1].axis('off')
    
    # 3. Histograma RGB
    axes[2].hist(samples[:, 0], bins=50, alpha=0.5, color='red', label='R')
    axes[2].hist(samples[:, 1], bins=50, alpha=0.5, color='green', label='G')
    axes[2].hist(samples[:, 2], bins=50, alpha=0.5, color='blue', label='B')
    axes[2].axvline(samples[:, 0].mean(), color='red', linestyle='--', linewidth=2)
    axes[2].axvline(samples[:, 1].mean(), color='green', linestyle='--', linewidth=2)
    axes[2].axvline(samples[:, 2].mean(), color='blue', linestyle='--', linewidth=2)
    axes[2].set_title('Distribución RGB', fontsize=14)
    axes[2].set_xlabel('Valor (0-255)')
    axes[2].set_ylabel('Frecuencia')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_path = image_path.replace('.png', '_POSITION10_RGB.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\n✅ Visualización guardada: {output_path}")
    print("="*80)
    
    return {
        'r_min': r_min, 'r_max': r_max,
        'g_min': g_min, 'g_max': g_max,
        'b_min': b_min, 'b_max': b_max,
        'samples': samples
    }

if __name__ == "__main__":
    image_path = "debug_screenshots/map_initial_20260131_164303.png"
    position = [419, 331]  # Supply #10 - ÚNICO VÁLIDO
    
    # Probar radios MUY PEQUEÑOS para samplear SOLO el cubo del farolito
    print("🔍 SAMPLEANDO SOLO EL CUBO DEL FAROLITO (radios pequeños):\n")
    for radius in [1, 2, 3, 4]:
        print(f"\n{'='*80}")
        print(f"📏 RADIO: {radius} píxeles (SOLO CUBO)")
        print('='*80)
        rgb_data = sample_rgb_around_position(image_path, position, radius=radius)
    
    print("\n🎯 SIGUIENTE PASO:")
    print("   1. Revisar visualización RGB")
    print("   2. Aplicar nuevos rangos al código")
    print("   3. Re-detectar para ver si elimina falsos positivos")
    print("   4. Buscar eventos especiales (verdes) con método similar")
    print("="*80)
