"""
Script para visualizar el área del LAUNCH BUTTON donde aparece el cooldown
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

# Área del LAUNCH BUTTON ACTUAL: (650 / 831, 712 / 831, 132 / 481, 310 / 481)
# Esto es aproximadamente Y[78%-86%] X[27%-64%]
launch_y_start = int((650 / 831) * height)
launch_y_end = int((712 / 831) * height)
launch_x_start = int((132 / 481) * width)
launch_x_end = int((310 / 481) * width)

print(f"\n📦 ÁREA LAUNCH BUTTON ACTUAL:")
print(f"   Y[{launch_y_start}-{launch_y_end}] X[{launch_x_start}-{launch_x_end}]")
print(f"   Altura: {launch_y_end - launch_y_start}px")
print(f"   Ancho: {launch_x_end - launch_x_start}px")

# Dibujar área del launch button en ROJO
draw.rectangle(
    [(launch_x_start, launch_y_start), (launch_x_end, launch_y_end)],
    outline="red",
    width=3
)
draw.text((launch_x_start + 5, launch_y_start + 5), "LAUNCH BUTTON ACTUAL", fill="red")

# Proponer área EXPANDIDA HACIA ARRIBA para capturar el cooldown
# El texto "0m 9s" está MUCHO MÁS ARRIBA del botón
# Propongo expandir desde Y[78%] hasta Y[50%] (empezar MUCHO más arriba)
new_y_start = int((500 / 831) * height)  # ~60% (empezar MUCHO más arriba)
new_y_end = launch_y_end  # Mantener el final igual
new_x_start = launch_x_start  # Mantener X igual
new_x_end = launch_x_end

print(f"\n📦 ÁREA LAUNCH BUTTON PROPUESTA (EXPANDIDA):")
print(f"   Y[{new_y_start}-{new_y_end}] X[{new_x_start}-{new_x_end}]")
print(f"   Altura: {new_y_end - new_y_start}px (+{new_y_start - launch_y_start}px arriba)")
print(f"   Ancho: {new_x_end - new_x_start}px")

# Dibujar área expandida en VERDE
draw.rectangle(
    [(new_x_start, new_y_start), (new_x_end, new_y_end)],
    outline="green",
    width=3
)
draw.text((new_x_start + 5, new_y_start + 5), "EXPANDIDA (captura cooldown)", fill="green")

# Guardar imagen con las áreas marcadas
output_path = "debug_screenshots/launch_button_area_comparison.png"
img_visual.save(output_path)
print(f"\n✅ Imagen guardada: {output_path}")

# También crear imagen recortada del área nueva
new_area = img.crop((new_x_start, new_y_start, new_x_end, new_y_end))
new_area_path = "debug_screenshots/launch_button_area_nueva.png"
new_area.save(new_area_path)
print(f"✅ Área nueva recortada: {new_area_path}")

# Y del área anterior
old_area = img.crop((launch_x_start, launch_y_start, launch_x_end, launch_y_end))
old_area_path = "debug_screenshots/launch_button_area_anterior.png"
old_area.save(old_area_path)
print(f"✅ Área anterior recortada: {old_area_path}")

print("\n" + "="*60)
print("🔍 VERIFICACIÓN:")
print("="*60)
print("1. Abre: launch_button_area_comparison.png")
print("   - ROJO = área actual del launch button")
print("   - VERDE = área expandida (debe capturar '0m 9s')")
print("")
print("2. Verifica que el texto '0m 9s' esté en el área VERDE")
print("")
print("3. Confirma y ajustaremos launch_button_loc_ratio en el código")
print("="*60)
