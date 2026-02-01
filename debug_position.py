"""
Verificar por qué el farolito [200, 304] NO se detecta
"""

import numpy as np
import matplotlib.pyplot as plt
from skimage import measure, morphology

def check_position(image_path, position):
    """Verifica por qué una posición específica no se detecta"""
    
    print("="*80)
    print(f"🔍 VERIFICANDO POSICIÓN: {position}")
    print("="*80)
    
    # Cargar imagen
    img = plt.imread(image_path)
    
    # Convertir a RGB 0-255
    if img.max() <= 1.0:
        img_rgb = (img * 255).astype(np.uint8)
    else:
        img_rgb = img.astype(np.uint8)
    
    y, x = position
    
    # Obtener RGB en esa posición
    pixel_rgb = img_rgb[y, x, :3]
    print(f"\n📊 RGB en [{y}, {x}]: R={pixel_rgb[0]} G={pixel_rgb[1]} B={pixel_rgb[2]}")
    
    # Verificar rangos
    print("\n🔍 VERIFICACIÓN DE RANGOS:")
    print("-" * 80)
    
    # Verde
    verde_r = 10 <= pixel_rgb[0] <= 40
    verde_g = 200 <= pixel_rgb[1] <= 235
    verde_b = 5 <= pixel_rgb[2] <= 30
    verde_match = verde_r and verde_g and verde_b
    print(f"🟢 VERDE R[10-40] G[200-235] B[5-30]:")
    print(f"   R={pixel_rgb[0]} {'✅' if verde_r else '❌'}")
    print(f"   G={pixel_rgb[1]} {'✅' if verde_g else '❌'}")
    print(f"   B={pixel_rgb[2]} {'✅' if verde_b else '❌'}")
    print(f"   MATCH: {'✅ SÍ' if verde_match else '❌ NO'}")
    
    # Naranja
    naranja_r = 233 <= pixel_rgb[0] <= 255
    naranja_g = 120 <= pixel_rgb[1] <= 165
    naranja_b = 0 <= pixel_rgb[2] <= 30
    naranja_match = naranja_r and naranja_g and naranja_b
    print(f"\n🟠 NARANJA R[233-255] G[120-165] B[0-30]:")
    print(f"   R={pixel_rgb[0]} {'✅' if naranja_r else '❌'}")
    print(f"   G={pixel_rgb[1]} {'✅' if naranja_g else '❌'}")
    print(f"   B={pixel_rgb[2]} {'✅' if naranja_b else '❌'}")
    print(f"   MATCH: {'✅ SÍ' if naranja_match else '❌ NO'}")
    print("-" * 80)
    
    # Crear máscaras
    event_mask = (
        (img_rgb[:,:,0] >= 10) & (img_rgb[:,:,0] <= 40) &
        (img_rgb[:,:,1] >= 200) & (img_rgb[:,:,1] <= 235) &
        (img_rgb[:,:,2] >= 5) & (img_rgb[:,:,2] <= 30)
    )
    
    supply_mask = (
        (img_rgb[:,:,0] >= 233) & (img_rgb[:,:,0] <= 255) &
        (img_rgb[:,:,1] >= 120) & (img_rgb[:,:,1] <= 165) &
        (img_rgb[:,:,2] >= 0) & (img_rgb[:,:,2] <= 30)
    )
    
    combined = np.logical_or(event_mask, supply_mask).astype(np.uint8)
    
    print(f"\n🎭 MÁSCARA EN [{y}, {x}]:")
    print(f"   Verde: {event_mask[y, x]}")
    print(f"   Naranja: {supply_mask[y, x]}")
    print(f"   Combinada: {combined[y, x]}")
    
    # Aplicar morphology
    combined_morph = morphology.binary_closing(combined, np.ones((5,5)))
    
    print(f"\n⚙️  DESPUÉS DE MORPHOLOGY:")
    print(f"   Máscara: {combined_morph[y, x]}")
    
    # Etiquetar
    labels = measure.label(combined_morph)
    label_at_pos = labels[y, x]
    
    print(f"\n🏷️  ETIQUETADO:")
    print(f"   Label en [{y}, {x}]: {label_at_pos}")
    
    if label_at_pos > 0:
        # Contar píxeles del componente
        component_pixels = np.sum(labels == label_at_pos)
        print(f"   Tamaño del componente: {component_pixels} píxeles")
        print(f"   min_pixels requerido: 100")
        
        if component_pixels >= 100:
            print(f"   ✅ DEBERÍA DETECTARSE (componente >= 100px)")
        else:
            print(f"   ❌ RECHAZADO (componente < 100px)")
    else:
        print(f"   ❌ NO está en ningún componente conectado")
    
    print("="*80)

if __name__ == "__main__":
    image_path = "debug_screenshots/map_initial_20260131_164303.png"
    
    # Farolito que usamos para análisis RGB
    print("\n🧪 FAROLITO DE ANÁLISIS (debería detectarse):")
    check_position(image_path, [200, 304])
    
    # Verificar también los detectados correctos
    print("\n\n✅ FAROLITO DETECTADO CORRECTO:")
    check_position(image_path, [266, 314])  # Naranja #5
