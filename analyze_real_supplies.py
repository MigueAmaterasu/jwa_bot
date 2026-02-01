"""
Script para analizar el supply drop válido y encontrar los faltantes

Análisis:
1. Supply #10 [419, 331] - el ÚNICO válido de 42
2. Encontrar los otros 10 supplies que el usuario vio pero NO fueron detectados
3. Analizar tamaños y valores RGB de los reales
4. Recomendar nuevos rangos de color

Uso:
    python analyze_real_supplies.py
"""

import numpy as np
import matplotlib.pyplot as plt
from skimage import measure, morphology

def analyze_detected_supply(image_path, position):
    """Analiza el supply detectado #10"""
    
    print("="*80)
    print(f"🔍 ANALIZANDO SUPPLY #10 (ÚNICO VÁLIDO)")
    print("="*80)
    print(f"Posición: {position}\n")
    
    # Cargar imagen
    img = plt.imread(image_path)
    y, x = position
    
    # Rangos de color actuales
    supply_color = (160, 60, 0, 255, 255, 120)
    
    # Crear máscara con rangos actuales
    mask = (
        (img[:,:,0] >= supply_color[0]/255) & (img[:,:,0] <= supply_color[3]/255) &
        (img[:,:,1] >= supply_color[1]/255) & (img[:,:,1] <= supply_color[4]/255) &
        (img[:,:,2] <= supply_color[5]/255)
    )
    
    # Encontrar componente que contiene (y, x)
    labels = measure.label(mask)
    if y < labels.shape[0] and x < labels.shape[1]:
        label_at_pos = labels[y, x]
        if label_at_pos > 0:
            component_mask = labels == label_at_pos
            rows, cols = np.where(component_mask)
            
            print(f"✅ Encontrado componente en posición {position}")
            print(f"   📏 Tamaño: {len(rows)} píxeles")
            print(f"   📐 Bounding box: Y[{rows.min()}-{rows.max()}] X[{cols.min()}-{cols.max()}]")
            print(f"   📊 Dimensiones: {rows.max()-rows.min()}x{cols.max()-cols.min()} px")
            
            # Samplear valores RGB del supply
            rgb_samples = img[component_mask]
            print(f"\n   🎨 Valores RGB del supply #10:")
            print(f"      R: min={rgb_samples[:,0].min()*255:.0f} max={rgb_samples[:,0].max()*255:.0f} avg={rgb_samples[:,0].mean()*255:.0f}")
            print(f"      G: min={rgb_samples[:,1].min()*255:.0f} max={rgb_samples[:,1].max()*255:.0f} avg={rgb_samples[:,1].mean()*255:.0f}")
            print(f"      B: min={rgb_samples[:,2].min()*255:.0f} max={rgb_samples[:,2].max()*255:.0f} avg={rgb_samples[:,2].mean()*255:.0f}")
            
            return len(rows), rgb_samples
    
    print(f"❌ No se encontró componente en posición {position}")
    return 0, None

def find_missing_supplies(image_path):
    """Busca supplies que el usuario vio pero el bot NO detectó"""
    
    print("\n" + "="*80)
    print("🔍 BUSCANDO SUPPLIES FALTANTES")
    print("="*80)
    print("Usuario contó: 11 supplies (8 naranjas + 3 verdes)")
    print("Bot detectó: 1 válido (#10)")
    print("Faltantes: 10 supplies\n")
    
    # Cargar imagen
    img = plt.imread(image_path)
    
    # Probar con rangos MÁS AMPLIOS para encontrar todos
    # Naranja: incluir más rojos y amarillos
    supply_mask = (
        (img[:,:,0] >= 140/255) &  # R más bajo
        (img[:,:,1] >= 40/255) &    # G más bajo
        (img[:,:,2] <= 150/255)     # B más alto
    )
    
    # Verde: eventos especiales
    event_mask = (
        (img[:,:,0] <= 200/255) &
        (img[:,:,1] >= 100/255) &
        (img[:,:,2] <= 200/255)
    )
    
    combined = np.logical_or(supply_mask, event_mask).astype(np.uint8)
    combined = morphology.binary_closing(combined, np.ones((5,5)))
    
    labels = measure.label(combined)
    regions = measure.regionprops(labels)
    
    # Filtrar por tamaño mínimo más alto
    large_supplies = []
    for region in regions:
        if region.area >= 200:  # Solo objetos grandes
            y, x = region.centroid
            large_supplies.append({
                'pos': [int(y), int(x)],
                'area': region.area,
                'bbox': region.bbox
            })
    
    # Ordenar por tamaño
    large_supplies.sort(key=lambda s: s['area'], reverse=True)
    
    print(f"🔍 Encontrados {len(large_supplies)} objetos grandes (>=200 px):\n")
    for i, supply in enumerate(large_supplies[:15], 1):  # Top 15
        print(f"   {i:2d}. Posición {supply['pos']} - {supply['area']} píxeles")
    
    return large_supplies

if __name__ == "__main__":
    image_path = "debug_screenshots/map_initial_20260131_164303.png"
    
    # Analizar el único supply válido
    size, rgb_samples = analyze_detected_supply(image_path, [419, 331])
    
    # Buscar supplies faltantes
    found_supplies = find_missing_supplies(image_path)
    
    print("\n" + "="*80)
    print("💡 RECOMENDACIONES:")
    print("="*80)
    if size > 0:
        print(f"1. El supply #10 tiene {size} píxeles")
        print(f"   → Umbral mínimo debería ser ~{int(size * 0.3)} píxeles")
        print(f"   → Actual es 15 píxeles (DEMASIADO BAJO)")
    
    print(f"\n2. Encontrados {len(found_supplies)} objetos grandes")
    print(f"   → Revisar Top 11 manualmente")
    print(f"   → Esos deberían ser los 11 supplies reales")
    
    print("\n3. Crear imagen marcando los Top 11 más grandes")
    print("   → Usuario confirma cuáles son reales")
    print("   → Samplear RGB de esos 11")
    print("   → Ajustar rangos basado en datos reales")
    print("="*80)
