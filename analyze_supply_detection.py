"""
Script de análisis para entender la detección de supply drops

Este script:
1. Analiza la imagen inicial del mapa (map_initial_*.png)
2. Cuenta supply drops naranjas vs verdes MANUALMENTE vs AUTOMÁTICAMENTE
3. Compara regiones OCR actuales vs óptimas
4. Recomienda ajustes a los rangos de color y regiones OCR

Uso:
    python analyze_supply_detection.py map_initial_YYYYMMDD_HHMMSS.png
"""

import sys
import cv2
import numpy as np
from PIL import Image
from skimage import measure, morphology

def detect_supply_drops(image, supply_color, event_color):
    """Detecta supply drops usando los rangos de color actuales"""
    
    # Crear máscara para supply drops (naranja)
    supply_mask = (
        (image[:,:,0] >= supply_color[0]) & (image[:,:,0] <= supply_color[3]) &
        (image[:,:,1] >= supply_color[1]) & (image[:,:,1] <= supply_color[4]) &
        (image[:,:,2] <= supply_color[5])
    )
    
    # Crear máscara para eventos especiales (verde)
    event_mask = (
        (image[:,:,0] <= event_color[0]) &
        (image[:,:,1] >= event_color[1]) & (image[:,:,1] <= event_color[4]) &
        (image[:,:,2] <= event_color[5])
    )
    
    # Combinar máscaras
    combined_mask = supply_mask | event_mask
    combined_mask = combined_mask.astype(np.uint8)
    
    # Aplicar morfología
    kernel = np.ones((5, 5), np.uint8)
    combined_mask = morphology.binary_closing(combined_mask, kernel)
    
    # Detectar componentes
    labeled = measure.label(combined_mask)
    regions = measure.regionprops(labeled)
    
    positions = []
    for region in regions:
        if region.area >= 15:  # Mínimo 15 píxeles
            y, x = region.centroid
            positions.append([int(y), int(x), region.area, "green" if event_mask[int(y), int(x)] else "orange"])
    
    return positions

def analyze_image(image_path):
    """Analiza una imagen del mapa"""
    
    print("="*80)
    print("📊 ANÁLISIS DE DETECCIÓN DE SUPPLY DROPS")
    print("="*80)
    print(f"\n📁 Imagen: {image_path}\n")
    
    # Cargar imagen
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Error: No se pudo cargar la imagen '{image_path}'")
        return
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w = img_rgb.shape[:2]
    
    print(f"📐 Dimensiones: {w}x{h} píxeles\n")
    
    # Rangos de color actuales (de jw_bot.py)
    supply_color = (160, 60, 0, 255, 255, 120)  # R[160-255] G[60-255] B[0-120]
    event_color = (0, 120, 0, 180, 255, 180)    # R[0-180] G[120-255] B[0-180]
    
    # Detectar supply drops
    print("🔍 Detectando supply drops automáticamente...\n")
    positions = detect_supply_drops(img_rgb, supply_color, event_color)
    
    # Separar por tipo
    orange_drops = [p for p in positions if p[3] == "orange"]
    green_drops = [p for p in positions if p[3] == "green"]
    
    print(f"🟠 Supply drops NARANJAS detectados: {len(orange_drops)}")
    print(f"🟢 Supply drops VERDES (eventos) detectados: {len(green_drops)}")
    print(f"📦 TOTAL detectado: {len(positions)}\n")
    
    # Mostrar los 10 más grandes de cada tipo
    print("🔝 Top 10 supply drops NARANJAS (por tamaño):")
    orange_sorted = sorted(orange_drops, key=lambda x: x[2], reverse=True)[:10]
    for i, (y, x, area, color) in enumerate(orange_sorted, 1):
        print(f"   {i}. Posición ({y}, {x}) - {area} píxeles")
    
    print("\n🔝 Top 10 eventos VERDES (por tamaño):")
    green_sorted = sorted(green_drops, key=lambda x: x[2], reverse=True)[:10]
    for i, (y, x, area, color) in enumerate(green_sorted, 1):
        print(f"   {i}. Posición ({y}, {x}) - {area} píxeles")
    
    # Crear imagen de visualización
    print("\n🎨 Generando imagen de visualización...")
    vis_img = img_rgb.copy()
    
    for y, x, area, color in positions:
        # Dibujar círculo en cada supply drop detectado
        circle_color = (0, 255, 0) if color == "green" else (255, 165, 0)
        cv2.circle(vis_img, (x, y), 15, circle_color, 2)
        cv2.putText(vis_img, str(area), (x-10, y-20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, circle_color, 1)
    
    # Guardar imagen
    output_path = image_path.replace(".png", "_analysis.png")
    Image.fromarray(vis_img).save(output_path)
    print(f"✅ Imagen guardada: {output_path}\n")
    
    print("="*80)
    print("📝 INSTRUCCIONES:")
    print("="*80)
    print("1. Abre la imagen original y cuenta MANUALMENTE:")
    print("   - ¿Cuántos supply drops NARANJAS ves?")
    print("   - ¿Cuántos eventos VERDES ves?")
    print("2. Compara con los números detectados automáticamente arriba")
    print("3. Abre la imagen _analysis.png para ver qué detectó el bot")
    print("4. Si hay diferencia, necesitamos ajustar los rangos de color")
    print("="*80)

def analyze_ocr_regions():
    """Analiza las regiones OCR de las capturas de debug"""
    
    print("\n" + "="*80)
    print("🔍 ANÁLISIS DE REGIONES OCR")
    print("="*80)
    
    import os
    debug_folder = "debug_screenshots"
    
    if not os.path.exists(debug_folder):
        print(f"\n⚠️  Carpeta '{debug_folder}/' no existe todavía")
        print("   Ejecuta el bot primero para generar capturas de debug\n")
        return
    
    # Buscar archivos de supply text
    supply_text_files = [f for f in os.listdir(debug_folder) if "supply_text.png" in f]
    
    if not supply_text_files:
        print(f"\n⚠️  No se encontraron archivos de supply_text en '{debug_folder}/'")
        print("   Ejecuta el bot primero para generar capturas de debug\n")
        return
    
    print(f"\n📁 Encontrados {len(supply_text_files)} archivos de supply_text")
    print("\n📊 Analizando tamaño de regiones OCR...\n")
    
    for filename in supply_text_files[:5]:  # Analizar solo los primeros 5
        img_path = os.path.join(debug_folder, filename)
        img = cv2.imread(img_path)
        if img is not None:
            h, w = img.shape[:2]
            print(f"   {filename}: {w}x{h} píxeles")
    
    print("\n💡 RECOMENDACIONES:")
    print("   - Región óptima de supply_text debería ser ~200-250px de ancho")
    print("   - Si la región es muy pequeña, el OCR no puede leer el texto")
    print("   - Si es muy grande, puede leer texto de UI que no queremos")
    print("="*80)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n❌ Error: Debes proporcionar la ruta de la imagen")
        print("\nUso:")
        print("   python analyze_supply_detection.py map_initial_YYYYMMDD_HHMMSS.png")
        print("\nEjemplo:")
        print("   python analyze_supply_detection.py map_initial_20260131_164303.png")
        print()
        
        # Intentar analizar regiones OCR si existen
        analyze_ocr_regions()
        sys.exit(1)
    
    image_path = sys.argv[1]
    analyze_image(image_path)
    
    # También analizar regiones OCR si existen
    analyze_ocr_regions()
