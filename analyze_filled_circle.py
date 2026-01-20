"""
Detecta círculos RELLENOS blancos (no bordes) - para el punto de mira del juego
"""
import cv2
import numpy as np
import os
import glob

def analyze_filled_white_circle(image_path):
    """Detecta círculos RELLENOS de blanco (no bordes)"""
    
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ No se pudo leer: {image_path}")
        return None
    
    print(f"\n📸 Analizando: {os.path.basename(image_path)}")
    print(f"   Tamaño imagen: {img.shape[1]}x{img.shape[0]}")
    
    # ===========================================================================
    # ESTRATEGIA: Buscar REGIONES RELLENAS de blanco (no bordes)
    # ===========================================================================
    
    # 1. Crear máscara de píxeles blancos puros
    lower_white = np.array([240, 240, 240])  # BGR - muy blanco
    upper_white = np.array([255, 255, 255])
    mask_white = cv2.inRange(img, lower_white, upper_white)
    
    # 2. Encontrar contornos en la máscara blanca
    contours, _ = cv2.findContours(mask_white, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    print(f"   🔍 Contornos blancos detectados: {len(contours)}")
    
    filled_white_circles = []
    
    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        
        # Filtrar contornos muy pequeños (ruido)
        if area < 10:
            continue
        
        # Obtener bounding box
        x, y, w, h = cv2.boundingRect(contour)
        
        # Verificar si es aproximadamente circular (relación aspecto ~1.0)
        aspect_ratio = float(w) / h if h > 0 else 0
        is_circular = 0.7 <= aspect_ratio <= 1.3
        
        # Calcular "circularidad" (4π*area / perimeter²)
        # Círculo perfecto = 1.0, cuadrado = 0.785
        perimeter = cv2.arcLength(contour, True)
        circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
        
        # Radio estimado
        radius = int(np.sqrt(area / np.pi))
        center_x = x + w // 2
        center_y = y + h // 2
        
        # Filtrar solo círculos PEQUEÑOS (el puntito blanco es 3-30px, puede ser más pequeño con dinos raros)
        # Rechazar círculos grandes (>30px) que son ruido del juego
        if is_circular and circularity > 0.6 and 20 < area < 3000 and 3 <= radius <= 30:
            filled_white_circles.append({
                'center': (center_x, center_y),
                'radius': radius,
                'area': area,
                'circularity': circularity,
                'aspect_ratio': aspect_ratio
            })
            
            # Marcar en imagen
            cv2.circle(img, (center_x, center_y), radius, (0, 255, 0), 2)  # Verde
            cv2.circle(img, (center_x, center_y), 2, (0, 0, 255), 3)  # Rojo centro
            cv2.putText(img, f"R={radius}", (center_x + radius + 5, center_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
            
            print(f"   ⚪ CÍRCULO BLANCO RELLENO #{len(filled_white_circles)}:")
            print(f"      Centro: ({center_x}, {center_y})")
            print(f"      Radio: {radius}px")
            print(f"      Área: {area}px²")
            print(f"      Circularidad: {circularity:.3f}")
            print(f"      Relación aspecto: {aspect_ratio:.3f}")
    
    # Estadísticas
    white_pixels = np.sum(mask_white > 0)
    print(f"   📊 Píxeles blancos totales (>240): {white_pixels}")
    print(f"   ✅ Círculos blancos RELLENOS válidos: {len(filled_white_circles)}")
    
    # Guardar imagen anotada
    output_path = image_path.replace('.png', '_filled_analyzed.png')
    cv2.imwrite(output_path, img)
    
    # También guardar la máscara para debugging
    mask_path = image_path.replace('.png', '_mask.png')
    cv2.imwrite(mask_path, mask_white)
    
    print(f"   💾 Guardado: {os.path.basename(output_path)}")
    print(f"   💾 Máscara: {os.path.basename(mask_path)}")
    
    return filled_white_circles


def main():
    """Analiza TODAS las imágenes originales de shooting"""
    
    print("="*80)
    print("🎯 ANÁLISIS DE CÍRCULOS BLANCOS RELLENOS (Punto de mira)")
    print("="*80)
    
    # Buscar SOLO imágenes originales (no las ya analizadas)
    patterns = [
        "debug_screenshots/shooting_before_shot_202*.png",
        "debug_screenshots/shooting_start_202*.png",
        "debug_screenshots/shooting_tracking_202*.png"
    ]
    
    all_images = []
    for pattern in patterns:
        images = glob.glob(pattern)
        # Filtrar solo originales (no las que tienen _analyzed, _mask, etc)
        originals = [img for img in images if not any(x in img for x in ['_analyzed', '_mask', '_filled'])]
        all_images.extend(originals)
    
    # Ordenar por nombre
    all_images.sort()
    
    print(f"📁 Encontradas {len(all_images)} imágenes ORIGINALES para analizar")
    
    if not all_images:
        print("❌ No se encontraron imágenes de shooting")
        return
    
    all_results = []
    for img_path in all_images:
        result = analyze_filled_white_circle(img_path)
        if result:
            all_results.append({
                'image': os.path.basename(img_path),
                'circles': result
            })
    
    # Resumen final
    print("\n" + "="*80)
    print("📊 RESUMEN DE DETECCIÓN")
    print("="*80)
    
    for res in all_results:
        print(f"\n📷 {res['image']}")
        if res['circles']:
            for i, circle in enumerate(res['circles'], 1):
                print(f"   ⚪ Círculo #{i}: Centro=({circle['center'][0]}, {circle['center'][1]}) Radio={circle['radius']}px")
        else:
            print(f"   ❌ No se detectó círculo blanco pequeño")
    
    print("\n" + "="*80)
    print("✅ Análisis completo")
    print("💡 Revisa las imágenes *_filled_analyzed.png para ver los círculos detectados")
    print("💡 Revisa las imágenes *_mask.png para ver la máscara de blancos")
    print("="*80)


if __name__ == "__main__":
    main()
