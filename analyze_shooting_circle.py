"""
Analiza las imágenes de shooting para detectar el círculo blanco del punto de mira
"""
import cv2
import numpy as np
from PIL import Image
import os
import glob

def analyze_white_circle(image_path):
    """Analiza una imagen para detectar el círculo blanco"""
    
    # Leer imagen
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ No se pudo leer: {image_path}")
        return None
    
    print(f"\n📸 Analizando: {os.path.basename(image_path)}")
    print(f"   Tamaño imagen: {img.shape[1]}x{img.shape[0]}")
    
    # Convertir a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Detectar círculos usando HoughCircles
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=20,
        param1=50,
        param2=30,
        minRadius=3,    # Círculo pequeño mínimo
        maxRadius=100   # Círculo grande máximo
    )
    
    if circles is not None:
        circles = np.uint16(np.around(circles))
        print(f"   🔵 Círculos detectados: {len(circles[0])}")
        
        # Analizar cada círculo detectado
        for i, (x, y, r) in enumerate(circles[0]):
            # Obtener color promedio del círculo
            mask = np.zeros(gray.shape, np.uint8)
            cv2.circle(mask, (x, y), r, 255, -1)
            mean_color = cv2.mean(img, mask=mask)[:3]  # BGR
            
            # Verificar si es blanco (alto valor en todos los canales)
            is_white = all(c > 180 for c in mean_color)
            
            print(f"   Círculo #{i+1}: centro=({x},{y}) radio={r}px color_BGR={mean_color} {'⚪ BLANCO' if is_white else ''}")
            
            # Dibujar círculo para visualización
            if is_white:
                cv2.circle(img, (x, y), r, (0, 255, 0), 2)  # Verde
                cv2.circle(img, (x, y), 2, (0, 0, 255), 3)  # Rojo centro
    else:
        print("   ❌ No se detectaron círculos")
    
    # Intentar detectar píxeles blancos sin círculos
    # Rango para detectar blanco
    lower_white = np.array([200, 200, 200])  # BGR
    upper_white = np.array([255, 255, 255])
    
    mask_white = cv2.inRange(img, lower_white, upper_white)
    white_pixels = np.sum(mask_white > 0)
    
    print(f"   ⚪ Píxeles blancos totales: {white_pixels}")
    
    # Guardar imagen con círculos marcados
    output_path = image_path.replace('.png', '_analyzed.png')
    cv2.imwrite(output_path, img)
    print(f"   💾 Guardado: {os.path.basename(output_path)}")
    
    return circles

def main():
    print("="*80)
    print("🎯 ANÁLISIS DE CÍRCULO BLANCO EN SHOOTING")
    print("="*80)
    
    # Buscar imágenes de shooting
    patterns = [
        "debug_screenshots/shooting_before_shot_*.png",
        "debug_screenshots/shooting_start_*.png",
        "debug_screenshots/shooting_tracking_*.png"
    ]
    
    all_images = []
    for pattern in patterns:
        all_images.extend(glob.glob(pattern))
    
    all_images.sort()
    
    print(f"\n📁 Imágenes encontradas: {len(all_images)}")
    
    if not all_images:
        print("❌ No se encontraron imágenes de shooting")
        return
    
    # Analizar solo las primeras 5 imágenes para no saturar
    print(f"\n🔍 Analizando primeras 5 imágenes...")
    
    for img_path in all_images[:5]:
        analyze_white_circle(img_path)
    
    print("\n" + "="*80)
    print("✅ Análisis completo")
    print("💡 Revisa las imágenes *_analyzed.png para ver los círculos detectados")
    print("="*80)

if __name__ == "__main__":
    main()
