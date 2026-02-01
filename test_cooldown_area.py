"""
Script para definir el área correcta del cooldown time
Haz click en la esquina SUPERIOR IZQUIERDA del texto del tiempo
Luego haz click en la esquina INFERIOR DERECHA del texto del tiempo
"""
import cv2
import numpy as np
from PIL import Image
import pytesseract

# Cargar imagen
img_path = "debug_screenshots/supply_283_95_full_screen.png"
img = cv2.imread(img_path)
img_display = img.copy()

points = []

def mouse_callback(event, x, y, flags, param):
    global points, img_display
    
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        cv2.circle(img_display, (x, y), 5, (0, 255, 0), -1)
        
        if len(points) == 1:
            print(f"✅ Primer punto: ({x}, {y})")
            print("👉 Ahora haz click en la esquina INFERIOR DERECHA del texto")
        
        elif len(points) == 2:
            x1, y1 = points[0]
            x2, y2 = points[1]
            
            # Dibujar rectángulo
            cv2.rectangle(img_display, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Calcular coordenadas
            top = min(y1, y2)
            bottom = max(y1, y2)
            left = min(x1, x2)
            right = max(x1, x2)
            
            print("\n" + "="*60)
            print("📊 COORDENADAS DEL ÁREA:")
            print(f"   Y: [{top}, {bottom}]  (altura: {bottom-top}px)")
            print(f"   X: [{left}, {right}]  (ancho: {right-left}px)")
            print("="*60)
            
            # Extraer área
            area = img[top:bottom, left:right]
            
            # Guardar área
            cv2.imwrite("debug_screenshots/cooldown_area_test.png", area)
            print("✅ Área guardada en: debug_screenshots/cooldown_area_test.png")
            
            # Probar OCR
            area_rgb = cv2.cvtColor(area, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(area_rgb)
            text = pytesseract.image_to_string(pil_img, config='--psm 7').strip().upper()
            
            print("\n📝 RESULTADO OCR:")
            print(f"   '{text}'")
            
            # Calcular ratios (asumiendo pantalla 831x481)
            screen_h = 831
            screen_w = 481
            
            top_ratio = top / screen_h
            bottom_ratio = bottom / screen_h
            left_ratio = left / screen_w
            right_ratio = right / screen_w
            
            print("\n🔢 RATIOS (para jw_bot.py):")
            print(f"   self.cooldown_time_loc_ratio = ({top_ratio:.6f}, {bottom_ratio:.6f}, {left_ratio:.6f}, {right_ratio:.6f})")
            print(f"   self.cooldown_time_loc = ({top}, {bottom}, {left}, {right})")
            print("="*60)
            
            # Resetear
            points = []
            img_display = img.copy()
        
        cv2.imshow('Define Cooldown Area', img_display)

# Crear ventana
cv2.namedWindow('Define Cooldown Area')
cv2.setMouseCallback('Define Cooldown Area', mouse_callback)

print("="*60)
print("🎯 INSTRUCCIONES:")
print("="*60)
print("1. Busca el texto del TIEMPO de cooldown (ej: '14H 10M')")
print("2. Haz click en la esquina SUPERIOR IZQUIERDA del texto")
print("3. Haz click en la esquina INFERIOR DERECHA del texto")
print("4. El script te dará las coordenadas exactas")
print("5. Presiona 'q' para cerrar")
print("="*60)

cv2.imshow('Define Cooldown Area', img_display)

while True:
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cv2.destroyAllWindows()
