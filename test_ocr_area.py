"""
Script para visualizar las áreas de OCR sobre la imagen del supply drop con cooldown
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Cargar la imagen del supply drop con cooldown
img_path = "debug_screenshots/supply_413_422_full_screen.png"
if not os.path.exists(img_path):
    print(f"❌ No se encontró la imagen: {img_path}")
    exit(1)

img = Image.open(img_path)
width, height = img.size
print(f"📐 Tamaño de imagen: {width}x{height}px")

# Crear copia para dibujar
img_visual = img.copy()
draw = ImageDraw.Draw(img_visual)

# Área ANTERIOR (v3.2): Y[5%-15%] X[20%-80%]
old_y_start = int(0.05 * height)
old_y_end = int(0.15 * height)
old_x_start = int(0.20 * width)
old_x_end = int(0.80 * width)

print(f"\n📦 ÁREA ANTERIOR (v3.2):")
print(f"   Y[{old_y_start}-{old_y_end}] X[{old_x_start}-{old_x_end}]")
print(f"   Altura: {old_y_end - old_y_start}px")

# Dibujar área anterior en ROJO (la que NO capturaba el cooldown)
draw.rectangle(
    [(old_x_start, old_y_start), (old_x_end, old_y_end)],
    outline="red",
    width=3
)
draw.text((old_x_start + 5, old_y_start + 5), "ANTERIOR Y[5%-15%]", fill="red")

# Área NUEVA (v3.4.2): Y[2%-18%] X[20%-80%]
new_y_start = int(0.02 * height)
new_y_end = int(0.18 * height)
new_x_start = int(0.20 * width)
new_x_end = int(0.80 * width)

print(f"\n📦 ÁREA NUEVA (v3.4.2):")
print(f"   Y[{new_y_start}-{new_y_end}] X[{new_x_start}-{new_x_end}]")
print(f"   Altura: {new_y_end - new_y_start}px")
print(f"   Expansión: +{old_y_start - new_y_start}px arriba, +{new_y_end - old_y_end}px abajo")

# Dibujar área nueva en VERDE (la que SÍ captura el cooldown)
draw.rectangle(
    [(new_x_start, new_y_start), (new_x_end, new_y_end)],
    outline="green",
    width=3
)
draw.text((new_x_start + 5, new_y_start + 5), "NUEVA Y[2%-18%]", fill="green")

# Guardar imagen con las áreas marcadas
output_path = "debug_screenshots/ocr_area_comparison.png"
img_visual.save(output_path)
print(f"\n✅ Imagen guardada: {output_path}")
print(f"📸 Revisa la imagen para verificar que el área VERDE capture el texto '0m 9s'")

# También crear una imagen solo del área nueva recortada
new_area = img.crop((new_x_start, new_y_start, new_x_end, new_y_end))
new_area_path = "debug_screenshots/ocr_area_nueva_recortada.png"
new_area.save(new_area_path)
print(f"✅ Área recortada guardada: {new_area_path}")

# Y una del área anterior para comparar
old_area = img.crop((old_x_start, old_y_start, old_x_end, old_y_end))
old_area_path = "debug_screenshots/ocr_area_anterior_recortada.png"
old_area.save(old_area_path)
print(f"✅ Área anterior guardada: {old_area_path}")

print("\n" + "="*60)
print("🔍 INSTRUCCIONES:")
print("="*60)
print("1. Abre: ocr_area_comparison.png")
print("   - ROJO = área anterior (NO capturaba cooldown)")
print("   - VERDE = área nueva (SÍ debe capturar cooldown)")
print("")
print("2. Verifica que el texto '0m 9s' esté dentro del rectángulo VERDE")
print("")
print("3. Si el texto está fuera, ajustaremos los porcentajes")
print("="*60)
