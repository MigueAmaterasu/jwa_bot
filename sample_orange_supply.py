"""
Script para samplear el color RGB de un farolito NARANJA
Posición estimada cerca del #11 original: [419, 49]
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def sample_orange_supply(image_path, position, radius=3):
    """Samplea RGB del farolito naranja"""
    
    print("="*80)
    print(f"🟠 SAMPLEANDO RGB DEL FAROLITO NARANJA")
    print("="*80)
    print(f"📍 Posición estimada: {position}")
    print(f"📏 Radio de sampleo: {radius} píxeles (SOLO CUBO)\n")
    
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
    
    # Rangos recomendados
    r_min = max(0, int(samples[:, 0].mean() - 2*samples[:, 0].std()))
    r_max = min(255, int(samples[:, 0].mean() + 2*samples[:, 0].std()))
    g_min = max(0, int(samples[:, 1].mean() - 2*samples[:, 1].std()))
    g_max = min(255, int(samples[:, 1].mean() + 2*samples[:, 1].std()))
    b_min = max(0, int(samples[:, 2].mean() - 2*samples[:, 2].std()))
    b_max = min(255, int(samples[:, 2].mean() + 2*samples[:, 2].std()))
    
    print("\n💡 RANGOS RECOMENDADOS (Mean ± 2×Std):")
    print("-" * 80)
    print(f"R: [{r_min}, {r_max}]")
    print(f"G: [{g_min}, {g_max}]")
    print(f"B: [{b_min}, {b_max}]")
    print("-" * 80)
    
    # Comparar con evento verde
    print("\n🔄 COMPARACIÓN:")
    print("-" * 80)
    print(f"Evento VERDE:     R[10-40]   G[200-235] B[5-30]")
    print(f"Supply NARANJA:   R[{r_min}-{r_max}] G[{g_min}-{g_max}] B[{b_min}-{b_max}]")
    print("-" * 80)
    
    # Visualización
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # Mapa completo
    axes[0].imshow(img)
    circle = patches.Circle((x, y), radius, linewidth=3, 
                           edgecolor='orange', facecolor='none')
    axes[0].add_patch(circle)
    axes[0].plot(x, y, 'r+', markersize=20, markeredgewidth=3)
    axes[0].set_title(f'Farolito Naranja - Posición [{y}, {x}]', fontsize=14)
    axes[0].axis('off')
    
    # Zoom
    margin = 50
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
    axes[2].set_xlabel('Valor (0-255)')
    axes[2].set_ylabel('Frecuencia')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_path = image_path.replace('.png', '_ORANGE_SUPPLY.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\n✅ Visualización guardada: {output_path}")
    print("="*80)
    
    return {
        'r_min': r_min, 'r_max': r_max,
        'g_min': g_min, 'g_max': g_max,
        'b_min': b_min, 'b_max': b_max
    }

if __name__ == "__main__":
    image_path = "debug_screenshots/map_initial_20260131_164303.png"
    
    # Posición #11 original: [479, 49]
    # Usuario dice: mover 2 círculos arriba (60px aprox) y un poco a la izquierda
    # Probando diferentes ajustes a la izquierda
    print("🔍 PROBANDO AJUSTES FINOS A LA IZQUIERDA:\n")
    
    base_y = 419
    base_x = 49
    
    for x_offset in [0, -3, -5, -8]:
        position = [base_y, base_x + x_offset]
        print(f"\n{'='*80}")
        print(f"📍 Posición: [{position[0]}, {position[1]}] (offset X: {x_offset})")
        print('='*80)
        rgb_data = sample_orange_supply(image_path, position, radius=3)
    
    print("\n🎯 SIGUIENTE PASO:")
    print("   1. Verificar en la imagen si es el cubo naranja correcto")
    print("   2. Si no es correcto, ajustar la posición manualmente")
    print("   3. Una vez confirmado, aplicar rangos al código")
    print("="*80)
