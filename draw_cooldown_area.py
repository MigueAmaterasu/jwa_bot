"""
Script para visualizar dónde estamos buscando el cooldown time
"""
import cv2
import numpy as np

# Cargar imagen
img_path = "debug_screenshots/supply_283_95_full_screen.png"
img = cv2.imread(img_path)
img_display = img.copy()

# Obtener dimensiones
height, width = img.shape[:2]
print(f"📐 Dimensiones de la imagen: {width}x{height}")

# Coordenadas actuales que estamos usando
# cooldown_time_loc = (580, 640, 140, 300)  # Y[580-640] X[140-300]
current_y1, current_y2, current_x1, current_x2 = 580, 640, 140, 300

# Dibujar área ACTUAL en ROJO
cv2.rectangle(img_display, (current_x1, current_y1), (current_x2, current_y2), (0, 0, 255), 3)
cv2.putText(img_display, "ACTUAL", (current_x1, current_y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

# Área del botón LAUNCH (para referencia) - en VERDE
launch_y1, launch_y2, launch_x1, launch_x2 = 650, 712, 132, 310
cv2.rectangle(img_display, (launch_x1, launch_y1), (launch_x2, launch_y2), (0, 255, 0), 2)
cv2.putText(img_display, "LAUNCH BUTTON", (launch_x1, launch_y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

# Proponer área para texto ROJO LARGO - en AZUL
# El texto de cooldown ROJO ocupa casi todo el ancho de la pantalla
# Está en la misma posición Y del botón LAUNCH pero MUCHO MÁS ANCHO
proposed_y1 = launch_y1 - 10  # Justo arriba del botón LAUNCH
proposed_y2 = launch_y2 + 10  # Un poco más grande verticalmente
proposed_x1 = 50              # Casi desde el borde izquierdo
proposed_x2 = width - 50      # Casi hasta el borde derecho

cv2.rectangle(img_display, (proposed_x1, proposed_y1), (proposed_x2, proposed_y2), (255, 0, 0), 3)
cv2.putText(img_display, "PROPUESTA", (proposed_x1, proposed_y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

print("\n" + "="*60)
print("🎨 ÁREAS DIBUJADAS:")
print("="*60)
print(f"🔴 ROJO (ACTUAL):      Y[{current_y1}, {current_y2}] X[{current_x1}, {current_x2}]")
print(f"                       Altura: {current_y2-current_y1}px, Ancho: {current_x2-current_x1}px")
print()
print(f"🟢 VERDE (LAUNCH BTN): Y[{launch_y1}, {launch_y2}] X[{launch_x1}, {launch_x2}]")
print(f"                       Altura: {launch_y2-launch_y1}px, Ancho: {launch_x2-launch_x1}px")
print()
print(f"🔵 AZUL (PROPUESTA):   Y[{proposed_y1}, {proposed_y2}] X[{proposed_x1}, {proposed_x2}]")
print(f"                       Altura: {proposed_y2-proposed_y1}px, Ancho: {proposed_x2-proposed_x1}px")
print(f"                       (Texto ROJO largo, casi todo el ancho)")
print("="*60)

# Guardar imagen con las áreas marcadas
output_path = "debug_screenshots/cooldown_areas_comparison.png"
cv2.imwrite(output_path, img_display)
print(f"\n✅ Imagen guardada en: {output_path}")
print("\n👉 Abre la imagen y dime:")
print("   - ¿El rectángulo AZUL cubre el texto ROJO del cooldown?")
print("   - ¿Necesita ajustes?")
print("="*60)

# Abrir automáticamente
import subprocess
subprocess.run(["open", output_path])

