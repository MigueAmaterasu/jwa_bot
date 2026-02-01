"""
Script para probar los NUEVOS rangos RGB en la imagen
Debe detectar 11 supplies (8 naranjas + 3 verdes)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from skimage import measure, morphology

def test_new_ranges(image_path):
    """Detecta supplies con los nuevos rangos RGB reales"""
    
    print("="*80)
    print("🧪 PROBANDO NUEVOS RANGOS RGB v3.4.8.9.6")
    print("="*80)
    
    # Cargar imagen
    img = plt.imread(image_path)
    
    # Convertir a RGB 0-255
    if img.max() <= 1.0:
        img_rgb = (img * 255).astype(np.uint8)
    else:
        img_rgb = img.astype(np.uint8)
    
    print("\n📊 RANGOS CONFIGURADOS:")
    print("-" * 80)
    
    # NUEVOS rangos basados en análisis real
    print("🟢 EVENTO VERDE:")
    print("   RGB real: (22, 219, 13)")
    print("   Rangos: R[10-40] G[200-235] B[5-30]")
    event_mask = (
        (img_rgb[:,:,0] >= 10) & (img_rgb[:,:,0] <= 40) &
        (img_rgb[:,:,1] >= 200) & (img_rgb[:,:,1] <= 235) &
        (img_rgb[:,:,2] >= 5) & (img_rgb[:,:,2] <= 30)
    )
    
    print("\n🟠 SUPPLY NARANJA:")
    print("   RGB real: (255, 143, 18) y (255, 131, 4)")
    print("   Rangos: R[233-255] G[120-165] B[0-30]")
    supply_mask = (
        (img_rgb[:,:,0] >= 233) & (img_rgb[:,:,0] <= 255) &
        (img_rgb[:,:,1] >= 120) & (img_rgb[:,:,1] <= 165) &
        (img_rgb[:,:,2] >= 0) & (img_rgb[:,:,2] <= 30)
    )
    
    print("\n⚙️  PROCESAMIENTO:")
    print("   min_pixels: 70 (ajustado para supplies pequeños)")
    print("   Morphology: binary_closing 5x5")
    print("-" * 80)
    
    # Combinar máscaras
    combined = np.logical_or(event_mask, supply_mask).astype(np.uint8)
    combined = morphology.binary_closing(combined, np.ones((5,5)))
    
    # Etiquetar componentes
    labels = measure.label(combined)
    regions = measure.regionprops(labels)
    
    # Filtrar por tamaño mínimo = 70
    min_pixels = 70
    detections = []
    
    # ZONAS EXCLUIDAS (ajustadas - borde izquierdo más estrecho)
    excluded_zones = [
        # Barra inferior completa (botones del juego)
        {'name': 'Barra inferior completa', 'x_min': 0, 'x_max': 566, 'y_min': 630, 'y_max': 953},
        
        # Esquinas superiores (menú, notificaciones)
        {'name': 'Esquina superior izquierda', 'x_min': 0, 'x_max': 100, 'y_min': 0, 'y_max': 100},
        {'name': 'Esquina superior derecha', 'x_min': 466, 'x_max': 566, 'y_min': 0, 'y_max': 100},
        
        # Bordes laterales MÁS ESTRECHOS (solo UI extrema)
        {'name': 'Borde izquierdo', 'x_min': 0, 'x_max': 20, 'y_min': 0, 'y_max': 630},
        {'name': 'Borde derecho', 'x_min': 540, 'x_max': 566, 'y_min': 0, 'y_max': 630},
    ]
    
    for region in regions:
        if region.area >= min_pixels:
            y, x = region.centroid
            
            # Verificar si está en zona excluida
            is_excluded = False
            excluded_reason = ""
            for zone in excluded_zones:
                if (zone['x_min'] <= x <= zone['x_max'] and 
                    zone['y_min'] <= y <= zone['y_max']):
                    is_excluded = True
                    excluded_reason = zone['name']
                    break
            
            if is_excluded:
                print(f"   ⛔ EXCLUIDO: [{int(y)}, {int(x)}] en '{excluded_reason}'")
                continue
            
            # Determinar tipo (verde o naranja)
            if event_mask[int(y), int(x)]:
                tipo = "VERDE"
                color = "lime"
            elif supply_mask[int(y), int(x)]:
                tipo = "NARANJA"
                color = "orange"
            else:
                tipo = "MIXTO"
                color = "yellow"
            
            detections.append({
                'pos': [int(y), int(x)],
                'area': region.area,
                'tipo': tipo,
                'color': color
            })
    
    # Ordenar por Y (arriba a abajo)
    detections.sort(key=lambda d: d['pos'][0])
    
    # ELIMINAR DUPLICADOS (detecciones muy cercanas)
    print("\n🔍 ELIMINANDO DUPLICADOS:")
    print("-" * 80)
    filtered_detections = []
    for det in detections:
        is_duplicate = False
        for existing in filtered_detections:
            # Calcular distancia
            dist = ((det['pos'][0] - existing['pos'][0])**2 + 
                   (det['pos'][1] - existing['pos'][1])**2)**0.5
            if dist < 20:  # Mismo supply si están a menos de 20px
                print(f"   🗑️  DUPLICADO: {det['pos']} cerca de {existing['pos']} (dist={dist:.1f}px)")
                is_duplicate = True
                break
        
        if not is_duplicate:
            filtered_detections.append(det)
    
    detections = filtered_detections
    print(f"\n   ✅ Después de filtrar: {len(detections)} detecciones únicas")
    print("-" * 80)
    
    # Contar por tipo
    verdes = sum(1 for d in detections if d['tipo'] == "VERDE")
    naranjas = sum(1 for d in detections if d['tipo'] == "NARANJA")
    
    print(f"\n✅ RESULTADO:")
    print("=" * 80)
    print(f"   Total detectado: {len(detections)}")
    print(f"   🟢 Verdes:  {verdes}")
    print(f"   🟠 Naranjas: {naranjas}")
    print(f"\n   Esperado: 11 (3 verdes + 8 naranjas)")
    print("=" * 80)
    
    if len(detections) > 0:
        print(f"\n📋 LISTA DE DETECCIONES:")
        print("-" * 80)
        print(f"{'#':<4} {'Tipo':<10} {'Posición [Y, X]':<20} {'Tamaño (px)'}")
        print("-" * 80)
        
        for i, det in enumerate(detections, 1):
            print(f"{i:<4} {det['tipo']:<10} {str(det['pos']):<20} {det['area']}")
        
        print("-" * 80)
    
    # Crear visualización
    fig, ax = plt.subplots(1, 1, figsize=(12, 20))
    ax.imshow(img)
    ax.set_title(f'Nuevos Rangos RGB - Detectados: {len(detections)} (Esperado: 11)', 
                 fontsize=16, weight='bold')
    
    # Marcar cada detección
    for i, det in enumerate(detections, 1):
        y, x = det['pos']
        area = det['area']
        tipo = det['tipo']
        circle_color = det['color']
        
        # Círculo con color según tipo
        circle = patches.Circle((x, y), radius=20, linewidth=3, 
                               edgecolor=circle_color, facecolor='none')
        ax.add_patch(circle)
        
        # Etiqueta
        text = f"{i}\n{tipo}\n{area}px"
        ax.text(x-20, y-35, text, fontsize=10, color=circle_color,
               weight='bold',
               bbox=dict(boxstyle='round', facecolor='black', alpha=0.8))
    
    # Guardar
    output_path = image_path.replace('.png', '_NEW_RANGES.png')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\n✅ Imagen guardada: {output_path}")
    print("="*80)
    
    # Evaluación
    print(f"\n💡 EVALUACIÓN:")
    print("=" * 80)
    if len(detections) == 11:
        print("   ✅ PERFECTO: Detectados 11 supplies (igual que conteo manual)")
    elif len(detections) < 11:
        print(f"   ⚠️  FALTAN {11 - len(detections)} supplies")
        print("   → Rangos muy estrictos o supplies en zonas excluidas")
    else:
        print(f"   ⚠️  {len(detections) - 11} FALSOS POSITIVOS")
        print("   → Rangos muy amplios o min_pixels muy bajo")
    
    if verdes == 3:
        print(f"   ✅ Verdes correctos: {verdes}/3")
    else:
        print(f"   ❌ Verdes incorrectos: {verdes}/3 (esperado: 3)")
    
    if naranjas == 8:
        print(f"   ✅ Naranjas correctos: {naranjas}/8")
    else:
        print(f"   ❌ Naranjas incorrectos: {naranjas}/8 (esperado: 8)")
    
    print("="*80)
    
    return detections

if __name__ == "__main__":
    image_path = "debug_screenshots/map_initial_20260131_164303.png"
    detections = test_new_ranges(image_path)
    
    print("\n🔍 POR FAVOR REVISAR:")
    print("   - Abre: debug_screenshots/map_initial_20260131_164303_NEW_RANGES.png")
    print("   - Verifica que los círculos estén en supplies reales")
    print("   - Círculos VERDES = eventos especiales")
    print("   - Círculos NARANJAS = supply drops normales")
    print("="*80)
