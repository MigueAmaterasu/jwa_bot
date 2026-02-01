import time
import logging
import os
from datetime import datetime

import matplotlib.pyplot as plt
import pyautogui
import keyboard
import numpy as np
from PIL import Image
import pytesseract
from skimage import measure, morphology, filters, feature, color, transform
from scipy import ndimage

# ============================================================================
# 🦖 JURASSIC WORLD ALIVE BOT - v3.4.8.9.8
# ============================================================================
# CHANGELOG:
# v3.4.8.9.8 (31-Ene-2026): 📸 Capturas debug + Limpieza completa del mapa
#   - CAPTURAS AUTOMÁTICAS: Guarda screenshots de cada detección
#     * Carpetas: debug_screenshots/{supplies,coins,dinos}/
#     * Formato: {tipo}_{timestamp}_{contador:03d}_n{cantidad}.png
#     * Visualización: Círculos verdes numerados en cada detección
#   - LÓGICA MEJORADA (main.py): Revisa mismas posiciones múltiples veces
#     * Escanea mapa → recolecta todo → vuelve a escanear (sin cambiar vista)
#     * Solo cambia vista cuando zona está 100% limpia (0 objetos válidos)
#     * Evita perder dinos que reaparecen o tienen cooldown corto
#   - PROPÓSITO: Análisis de ~40 runs para entrenar filtros con ejemplos reales
#
# v3.4.8.9.7 (31-Ene-2026): 🦕 Filtros Sobel optimizados para detección de dinos
#   - ANÁLISIS: 6 dinos reales identificados (63-2107px, ratios 0.55-1.67)
#   - FILTROS IMPLEMENTADOS:
#     * Área: 31-6321px (captura desde dinos pequeños hasta raids grandes)
#     * Aspect ratio: 0.30-1.97 (elimina objetos muy alargados o muy planos)
#   - REDUCCIÓN: 114 → 31 detecciones (72.8% menos falsos positivos)
#   - MEJORA: Precisión de 5.3% → 19.4% (+14.1 puntos)
#   - RESULTADO: Bot pierde menos tiempo haciendo click en edificios/árboles
#   - NOTA: OCR post-click ya filtraba raids (palabras: JEFE/BOSS/NIVEL)
#
# v3.4.8.9.6 (31-Ene-2026): 🎨 Rangos RGB basados en análisis REAL de supplies
#   - ANÁLISIS: Sampleados píxeles exactos (radio 3px) de supplies reales
#   - EVENTO VERDE: RGB(22,219,13) → Rangos R[10-40] G[200-235] B[5-30]
#   - SUPPLY NARANJA: RGB(255,143,18) y RGB(255,131,4) → R[233-255] G[120-165] B[0-30]
#   - min_pixels: 15 → 100 → 70 (captura supplies pequeños de 78px)
#   - Zonas excluidas: Bordes ajustados (50px→20px izq, 516px→540px der)
#   - RESULTADO: 10/11 correctos (90.9% precisión vs 1/42 = 2.4% anterior)
#   - Problema anterior: Detectaba árboles (R alto, G bajo) en vez de supplies (R alto, G medio o G muy alto)
#
# v3.4.8.9.2 (31-Ene-2026): 🔴 BUG CRÍTICO CORREGIDO - Supply drops rechazados
#   - FIX: Reordenado checks en determine_state() para verificar "SUMINISTRO" ANTES de "ASALTO"
#   - PROBLEMA: Supply drops legítimos rechazados con "⛔ Incubadora o evento de combate"
#   - CAUSA: OCR leía "ACTUALIZACIÓN DE SUMINISTRO" → malinterpretaba "EVENTO DE ASALTO"
#   - SOLUCIÓN: Check de SUPPLY ahora tiene prioridad alta, se ejecuta antes de rechazar
#   - IMPACTO: De 8 detectados/0 recolectados → Ahora recolectará todos los legítimos
#
# v3.4.8.9.1 (31-Ene-2026): Debug logging para diagnosticar state comparison
# v3.4.8.9.0 (31-Ene-2026): Sistema híbrido 2 fases para dinos (tracking + rapid fire)
# v3.4.8.8.2 (30-Ene-2026): Fix infinite loop en supply collection (3 clicks + close)
# v3.4.8.8.1 (30-Ene-2026): Restaurado background_changed check (skip empty clicks)
# v3.4.8.8.0 (29-Ene-2026): OCR garbage validation + expanded excluded zones
# ============================================================================

# ============================================================================
# CONFIGURACIÓN DE TESSERACT
# ============================================================================
# Para BlueStacks en Windows, descomenta y ajusta la siguiente línea:
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
# 
# # Para macOS con Homebrew:
# pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'
#
# Si tesseract está en el PATH del sistema, puedes comentar/eliminar esta línea
# ============================================================================

# ============================================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================================
def setup_logging(log_level=logging.INFO):
    """
    Configura el sistema de logging para el bot
    Crea archivo de log con timestamp y muestra en consola
    """
    # Crear carpeta de logs si no existe
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Nombre del archivo con timestamp
    log_filename = f'logs/bot_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    
    # Configurar formato
    log_format = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para archivo
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setFormatter(log_format)
    file_handler.setLevel(logging.DEBUG)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    console_handler.setLevel(log_level)
    
    # Configurar logger principal
    logger = logging.getLogger('JWA_Bot')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info("="*80)
    logger.info("🦖 JURASSIC WORLD ALIVE BOT - INICIADO")
    logger.info("="*80)
    logger.info(f"📁 Log guardado en: {log_filename}")
    
    return logger

# Crear logger global
logger = setup_logging()
# ============================================================================


class Bot:

    def __init__(self, max_run_hours=None):
        # stores location of the app
        self.x, self.y, self.w, self.h = -1, -1, -1, -1
        self.loc = False
        
        # Logger
        self.logger = logging.getLogger('JWA_Bot')
        self.logger.info("🔧 Inicializando Bot...")
        
        # Tiempo límite de ejecución (en horas)
        self.max_run_hours = max_run_hours
        self.start_time = time.time()
        if max_run_hours:
            self.logger.info(f"⏱️  Tiempo límite configurado: {max_run_hours} horas")
        else:
            self.logger.info("⏱️  Sin límite de tiempo (correrá indefinidamente)")
        
        # Crear carpeta para debug screenshots
        if not os.path.exists('debug_screenshots'):
            os.makedirs('debug_screenshots')
            self.logger.info("📁 Carpeta 'debug_screenshots' creada")
        
        # Crear subcarpetas para capturas por tipo
        for folder in ['supplies', 'coins', 'dinos']:
            folder_path = os.path.join('debug_screenshots', folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
        
        # Contadores para nombrar capturas
        self.supply_counter = 0
        self.coin_counter = 0
        self.dino_counter = 0


        # get the ratios (I get it from my PC to fit other screen sizes)
        self.shooting_zone_ratio = (230 / 831, 740 / 971, 10 / 481, 410 / 481)
        
        # 🚀 LAUNCH BUTTON - Área para detectar botón "LANZAR" (dinos) y "ABRIR" (supply drops)
        # REVERTIDO a valores originales - el área expandida rompió el OCR
        self.launch_button_loc_ratio = (650 / 831, 712 / 831, 132 / 481, 310 / 481)
        
        # ⏱️ v3.4.3: NUEVA ÁREA DEDICADA solo para detectar cooldown "0m 9s"
        # Esta área escanea ARRIBA del botón donde aparece el tiempo restante
        # Coordenadas: Y[55%-70%] X[27%-64%] - justo arriba del launch button
        self.cooldown_text_loc_ratio = (450 / 831, 580 / 831, 132 / 481, 310 / 481)
        
        # ✅ CORREGIDO v3.2: Área del texto en la PARTE SUPERIOR de la pantalla
        # Esta área captura el texto "EVENTO", "SUMINISTRO", etc. que aparece ARRIBA de la cajita
        # Coordenadas: Y[5%-15%] X[20%-80%] de la pantalla
        self.supply_drop_text_loc_ratio = (0.05, 0.15, 0.20, 0.80)
        
        self.map_button_loc_ratio = (786 / 831, 222 / 481)
        self.battery_loc_ratio = (75 / 831, 76 / 831, 360 / 481, 420 / 481)
        self.dino_loading_screen_loc_ratio = (210 / 831, 230 / 481)  
        self.moved_too_far_loc_ratio = (551 / 831, 165 / 481)
        self.dino_shoot_loc_ratio = (250 / 831, 440 / 481)
        self.dart_loc_ratio = (428 / 831, 225 / 481)
        self.supply_drop_resources_text_loc_ratio = (170 / 890, 240 / 890, 110 / 515, 370 / 515)
        self.supply_drop_resources_amount_loc_ratio = (510 / 890, 565 / 890, 180 / 515, 310 / 515)
        self.dino_collected_text_loc_ratio = (160 / 891, 270 / 891, 50 / 513, 460 / 513)
        # self.dino_collected_text_loc_ratio = (160 / 891, 340 / 891, 50 / 513, 460 / 513)

        self.dino_collected_amount_loc_ratio = (280 / 891, 330 / 891, 210 / 513, 350 / 513)
        self.center_loc_ratio = (587 / 954, 257 / 550)

        # pos - x and y change due to image (row = y, col = x)
        # (y_min, y_max, x_min, x_max)
        # (y, x)
        self.shooting_zone = (230, 720, 10, 440)
        self.launch_button_loc = (650, 712, 132, 310)
        self.supply_drop_text_loc = (150, 250, 80, 400)  # CORREGIDO: área más grande y centrada
        self.map_button_loc = (786, 222)
        self.battery_loc = (75, 76, 360, 420)
        self.dino_loading_screen_loc = (210, 230)
        self.moved_too_far_loc = (551, 165)
        self.dino_shoot_loc = (250, 440)
        self.dart_loc = (428, 225)
        self.supply_drop_resources_text_loc = (170, 240, 110, 370)
        self.dino_collected_text_loc = (160, 270, 50, 460)
        self.dino_collected_amount_loc = (280, 330, 220, 350)
        self.center_loc = (587, 257)
        self.D = 10
        self.v_max = 30  # ⚡ v3.4.8: TRIPLICADO (10→20→30) para seguir dinos ultra-rápidos
        

        # ========================================================================
        # CONFIGURACIÓN DE COLORES RGB PARA DETECCIÓN
        # ========================================================================
        # Formato: (R_min, G_min, B_min, R_max, G_max, B_max)
        # Los píxeles que estén dentro de este rango serán detectados
        # 
        # 💡 CÓMO AJUSTAR:
        # 1. Toma una captura de pantalla de BlueStacks con el objeto visible
        # 2. Usa un color picker (ej: GIMP, Photoshop, Paint) para obtener RGB
        # 3. Ajusta los rangos min/max para incluir variaciones de brillo
        # 
        # 🎨 COLORES ACTIVOS (basados en análisis RGB real v3.4.8.9.6):
        
        # 🟢 EVENTOS ESPECIALES - Verde brillante
        # Análisis real: RGB(22, 219, 13) - Radio 3px
        self.special_event_color = (10, 200, 5, 40, 235, 30)
        # Rango: R[10-40], G[200-235], B[5-30]
        
        # 🟠 SUPPLY DROPS - Naranja (rojo alto)
        # Análisis real: RGB(255, 143, 18) y RGB(255, 131, 4) - Radio 3px
        self.supply_drop_color = (233, 120, 0, 255, 165, 30)
        # Rango: R[233-255], G[120-165], B[0-30]
        
        # ========================================================================
        # 🎨 COLORES ALTERNATIVOS PARA EVENTOS ESPECIALES
        # Descomenta el evento que esté activo en tu juego
        # ========================================================================
        
        # 🧧 LUNAR NEW YEAR (Año Nuevo Lunar)
        # self.special_event_color = (170, 140, 50, 230, 190, 100)
        # self.supply_drop_color = (150, 120, 0, 255, 180, 60)
        
        # 💝 VALENTINE'S DAY (San Valentín)
        # self.special_event_color = (0, 140, 0, 100, 255, 100)
        # self.supply_drop_color = (180, 0, 0, 255, 100, 120)
        
        # ❄️ ST. PETERSBURG / WINTER (Invierno)
        # self.special_event_color = (0, 140, 0, 45, 255, 45)
        # self.supply_drop_color = (60, 60, 0, 210, 210, 120)
        
        # ========================================================================
        
        # ❌ BOTÓN X (para cerrar ventanas) - Rojo oscuro
        self.x_button_color = (117, 10, 10)
        
        # 📍 UBICACIÓN EN GOOGLE MAPS - Rojo brillante
        self.gmap_loc_color = (200, 0, 0, 255, 70, 60)
        
        # ========================================================================
        # 🪙 MONEDAS / COIN CHASE
        # ========================================================================
        
        # 🟡 DEFAULT - Dorado brillante
        self.coin_color = (180, 160, 100, 240, 220, 120)
        # Rango: R[180-240], G[160-220], B[100-120]
        
        # 🧧 LUNAR NEW YEAR
        # self.coin_color = (200, 50, 20, 255, 140, 50)
        
        # ❄️ WINTER GAMES / FESTIVAL - Azul
        # self.coin_color = (20, 35, 130, 95, 95, 170)
        
        # 💝 VALENTINE
        # self.coin_color = (180, 0, 0, 255, 100, 120)
        
        # 🎪 ALGO MÁS - Gris/Plateado
        # self.coin_color = (130, 150, 150, 175, 175, 200)
        # self.coin_color = (175, 175, 150, 225, 225, 225)
        
        # ========================================================================
        
        # 🔋 BATERÍA DE DARDOS - Azul oscuro
        self.battery_color = (10, 30, 80)
        
        # 📱 PANTALLA DE CARGA DINOSAURIO - Blanco brillante
        self.dino_loading_screen_color = (230, 230, 230)

        # other
        self.number_of_scrolls = 0
        self.max_click = 4
        self.custom_config = r'--oem 3 --psm 1'

        # extra stuff
        self.loading_screen_pic = Image.open(r'figs/loading_screen.png')
        #self.moved_too_far_pic = Image.open(r'figs/moved_too_far.PNG')

        # self.coin_chests = [
        #     np.array(Image.open(r'figs/lunar_event_coin_chase_1.png')),
        #     np.array(Image.open(r'figs/lunar_event_coin_chase_2.png')),
        #     np.array(Image.open(r'figs/lunar_event_coin_chase_3.png')),
        #     np.array(Image.open(r'figs/lunar_event_coin_chase_4.png')),
        #     np.array(Image.open(r'figs/lunar_event_coin_chase_5.png')),
        # ]

        # self.default_size = ()

        # supply drop templates

        # 
        self.supply_collected = {}
        self.dino_collected = {}


    def set_app_loc(self, x, y, w, h):
        

        # background = np.array(pyautogui.screenshot())
        # fig = plt.figure()
        # plt.imshow(background)
        # plt.title("CLICK TOP RIGHT CORNER THEN BOTTOM LEFT", fontsize=15)


        # def onclick(event):
        #     # print(event)

        #     if self.x == -1 or self.y == -1:
        #         self.x, self.y = event.xdata, event.ydata
        #     elif self.w == -1 or self.h == -1:
        #         self.w = event.xdata - self.x
        #         self.h = event.ydata - self.y
        #         print("DONE")
        #         print("LOC :", self.x, self.y, "SIZE :", self.w, self.h)
        #         fig.canvas.mpl_disconnect(cid)
        #         plt.close()

        # cid = fig.canvas.mpl_connect('button_press_event', onclick)
        # plt.show()

        self.x, self.y, self.w, self.h = x, y, w, h
        
        self.logger.info("="*80)
        self.logger.info("📐 CONFIGURACIÓN DE VENTANA BLUESTACKS")
        self.logger.info("="*80)
        self.logger.info(f"📍 Posición X: {self.x}px")
        self.logger.info(f"📍 Posición Y: {self.y}px")
        self.logger.info(f"📏 Ancho (W): {self.w}px")
        self.logger.info(f"📏 Alto (H): {self.h}px")
        self.logger.info(f"🎯 Esquina superior izquierda: ({self.x}, {self.y})")
        self.logger.info(f"🎯 Esquina inferior derecha: ({self.x + self.w}, {self.y + self.h})")
        self.logger.info("="*80)

        self.loc = True

        # set location according to my screen little bit off is fine
        self.shooting_zone = (int(self.shooting_zone_ratio[0]*h), 
                              int(self.shooting_zone_ratio[1]*h), 
                              int(self.shooting_zone_ratio[2]*w), 
                              int(self.shooting_zone_ratio[3]*w))
        self.logger.info(f"🎯 Shooting zone: Y[{self.shooting_zone[0]}-{self.shooting_zone[1]}] X[{self.shooting_zone[2]}-{self.shooting_zone[3]}]")
        
        self.launch_button_loc = (int(self.launch_button_loc_ratio[0]*h), 
                                  int(self.launch_button_loc_ratio[1]*h),
                                  int(self.launch_button_loc_ratio[2]*w),
                                  int(self.launch_button_loc_ratio[3]*w))
        self.logger.info(f"🚀 Launch button: Y[{self.launch_button_loc[0]}-{self.launch_button_loc[1]}] X[{self.launch_button_loc[2]}-{self.launch_button_loc[3]}]")
        
        # ⏱️ Nueva área para detectar cooldown
        self.cooldown_text_loc = (int(self.cooldown_text_loc_ratio[0]*h),
                                  int(self.cooldown_text_loc_ratio[1]*h),
                                  int(self.cooldown_text_loc_ratio[2]*w),
                                  int(self.cooldown_text_loc_ratio[3]*w))
        self.logger.info(f"⏱️  Cooldown text area: Y[{self.cooldown_text_loc[0]}-{self.cooldown_text_loc[1]}] X[{self.cooldown_text_loc[2]}-{self.cooldown_text_loc[3]}]")
        
        self.supply_drop_text_loc = (int(self.supply_drop_text_loc_ratio[0]*h),
                                     int(self.supply_drop_text_loc_ratio[1]*h),
                                     int(self.supply_drop_text_loc_ratio[2]*w),
                                     int(self.supply_drop_text_loc_ratio[3]*w))
        self.logger.info(f"📝 Supply text area: Y[{self.supply_drop_text_loc[0]}-{self.supply_drop_text_loc[1]}] X[{self.supply_drop_text_loc[2]}-{self.supply_drop_text_loc[3]}]")
        self.map_button_loc = (int(self.map_button_loc_ratio[0]*h), 
                               int(self.map_button_loc_ratio[1]*w))
        self.battery_loc = (int(self.battery_loc_ratio[0]*h),
                            int(self.battery_loc_ratio[1]*h),
                            int(self.battery_loc_ratio[2]*w),
                            int(self.battery_loc_ratio[3]*w))
        self.dino_loading_screen_loc = (int(self.dino_loading_screen_loc_ratio[0]*h), 
                                        int(self.dino_loading_screen_loc_ratio[1]*w))
        self.moved_too_far_loc = (int(self.moved_too_far_loc_ratio[0]*h), 
                                int(self.moved_too_far_loc_ratio[1]*w))
        self.dino_shoot_loc =(int(self.dino_shoot_loc_ratio[0]*h), 
                                int(self.dino_shoot_loc_ratio[1]*w))
        self.dart_loc = (int(self.dart_loc_ratio[0]*h), 
                        int(self.dart_loc_ratio[1]*w))
        self.supply_drop_resources_text_loc = (int(self.supply_drop_resources_text_loc_ratio[0]*h),
                                                int(self.supply_drop_resources_text_loc_ratio[1]*h),
                                                int(self.supply_drop_resources_text_loc_ratio[2]*w),
                                                int(self.supply_drop_resources_text_loc_ratio[3]*w))
        self.supply_drop_resources_amount_loc = (int(self.supply_drop_resources_amount_loc_ratio[0]*h),
                                                int(self.supply_drop_resources_amount_loc_ratio[1]*h),
                                                int(self.supply_drop_resources_amount_loc_ratio[2]*w),
                                                int(self.supply_drop_resources_amount_loc_ratio[3]*w))        
        self.dino_collected_text_loc = (int(self.dino_collected_text_loc_ratio[0]*h),
                                        int(self.dino_collected_text_loc_ratio[1]*h),
                                        int(self.dino_collected_text_loc_ratio[2]*w),
                                        int(self.dino_collected_text_loc_ratio[3]*w))
        self.dino_collected_amount_loc = (int(self.dino_collected_amount_loc_ratio[0]*h),
                                            int(self.dino_collected_amount_loc_ratio[1]*h),
                                            int(self.dino_collected_amount_loc_ratio[2]*w),
                                            int(self.dino_collected_amount_loc_ratio[3]*w))  
        self.center_loc = (int(self.center_loc_ratio[0]*h), int(self.center_loc_ratio[1]*w))
        self.D = 7 * h / 831 # 10 * h / 831
        self.v_max = 10 * h / 831

        # 📸 CAPTURA INICIAL: Guardar vista del mapa al inicio para analizar
        self.logger.info("📸 Capturando vista inicial del mapa para análisis...")
        time.sleep(0.5)  # Pequeña pausa para que se estabilice la pantalla
        
        background_initial = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            from PIL import Image
            debug_folder = "debug_screenshots"
            if not os.path.exists(debug_folder):
                os.makedirs(debug_folder)
            Image.fromarray(background_initial).save(f"{debug_folder}/map_initial_{timestamp}.png")
            self.logger.info(f"✅ Captura inicial guardada: map_initial_{timestamp}.png")
        except Exception as e:
            self.logger.warning(f"⚠️  Error al guardar captura inicial: {e}")

        # scroll down
        # pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2)
        # time.sleep(1)

        # background = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
        # pos = self.locate_x_button(background)
        # if pos:
        #     pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
        #     time.sleep(1)  

        # pyautogui.moveTo(self.x+self.w//2, self.y+self.h//2, 0.1)
        # pyautogui.keyDown('ctrl') 
        # time.sleep(0.1)
        # for _ in range(5):
        #     pyautogui.scroll(-90)
        #     time.sleep(0.5)
        # pyautogui.keyUp('ctrl')

    # ----------------------------------------------------------
    #   DETECTION
    # ----------------------------------------------------------

    # ----------------------------------------------------------
    #   DEBUG SCREENSHOTS
    # ----------------------------------------------------------
    
    def _save_detection_screenshot(self, background, positions, detection_type, counter):
        """Guarda screenshot con detecciones marcadas para análisis posterior
        
        Args:
            background: Imagen del mapa (numpy array)
            positions: Lista de posiciones detectadas [[row, col], ...]
            detection_type: Tipo de detección ("supply", "coin", "dino")
            counter: Contador para enumerar archivos
        """
        try:
            import cv2
            from datetime import datetime
            
            # Crear copia de la imagen para no modificar el original
            img_marked = background.copy()
            
            # Dibujar círculos en cada detección
            for i, pos in enumerate(positions, 1):
                row, col = pos[0], pos[1]
                # Círculo verde
                cv2.circle(img_marked, (col, row), 15, (0, 255, 0), 2)
                # Número
                cv2.putText(img_marked, str(i), (col - 10, row + 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            # Generar nombre de archivo con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"debug_screenshots/{detection_type}s/{detection_type}_{timestamp}_{counter:03d}_n{len(positions)}.png"
            
            # Guardar (OpenCV usa BGR, convertir de RGB)
            cv2.imwrite(filename, cv2.cvtColor(img_marked, cv2.COLOR_RGB2BGR))
            
        except Exception as e:
            self.logger.warning(f"⚠️  Error guardando screenshot debug: {e}")

    # ----------------------------------------------------------
    #   DETECTION
    # ----------------------------------------------------------

    def locate_x_button(self, background, button_color=None, shift=712):
        """Locate x button to go back to map"""

        if keyboard.is_pressed("q"):
            raise KeyboardInterrupt

        if button_color is None:
            button_color = self.x_button_color
            
        button = (background[shift:,:,0] == button_color[0]) * \
                (background[shift:,:,1] == button_color[1]) * \
                (background[shift:,:,2] == button_color[2])

        if np.sum(button) > 0:
            y, x = np.where(button)
            return shift + int(np.mean(y)), int(np.mean(x))
        return None
    
    def detect_supply_drop(self, background):
        """Finds supply drop by simply thresholding, but there might be false positives"""
        
        self.logger.debug("🔍 Buscando supply drops...")
        self.logger.debug(f"   📊 Supply color range: R[{self.supply_drop_color[0]}-{self.supply_drop_color[3]}] "
                         f"G[{self.supply_drop_color[1]}-{self.supply_drop_color[4]}] "
                         f"B[{self.supply_drop_color[2]}-{self.supply_drop_color[5]}]")
        self.logger.debug(f"   📊 Event color range: R[{self.special_event_color[0]}-{self.special_event_color[3]}] "
                         f"G[{self.special_event_color[1]}-{self.special_event_color[4]}] "
                         f"B[{self.special_event_color[2]}-{self.special_event_color[5]}]")

        if keyboard.is_pressed("q"):
            raise KeyboardInterrupt

        pos = []

        # threshold + clean up
        background_cropped = background[self.shooting_zone[0]:self.shooting_zone[1],
                                        self.shooting_zone[2]:self.shooting_zone[3]]
        
        self.logger.debug(f"   📐 Zona analizada: {background_cropped.shape}")
        
        t1 = (background_cropped[:,:,0] >= self.supply_drop_color[0]) * \
            (background_cropped[:,:,1] >= self.supply_drop_color[1]) * \
            (background_cropped[:,:,2] >= self.supply_drop_color[2]) * \
            (background_cropped[:,:,0] <= self.supply_drop_color[3]) * \
            (background_cropped[:,:,1] <= self.supply_drop_color[4]) * \
            (background_cropped[:,:,2] <= self.supply_drop_color[5])
        t2 = (background_cropped[:,:,0] >= self.special_event_color[0]) * \
            (background_cropped[:,:,1] >= self.special_event_color[1]) * \
            (background_cropped[:,:,2] >= self.special_event_color[2]) * \
            (background_cropped[:,:,0] <= self.special_event_color[3]) * \
            (background_cropped[:,:,1] <= self.special_event_color[4]) * \
            (background_cropped[:,:,2] <= self.special_event_color[5])
        
        mask = np.logical_or(t1, t2).astype(np.uint8)
        self.logger.debug(f"   🎨 Píxeles detectados inicialmente: {mask.sum()}")
        
        mask = morphology.binary_closing(mask, np.ones((5,5)))
        
        # connected components
        labels = measure.label(mask, background=0, connectivity=2)
        self.logger.debug(f"   🔢 Componentes detectados: {labels.max()}")

        # ⚡ v3.4.8.9.6: Umbral basado en análisis RGB real
        # Análisis real (31 Ene 2025):
        #   - Evento verde más pequeño: 141 píxeles
        #   - Supply naranja más pequeño: 78 píxeles (posición [201, 305])
        #   - Supply naranja típico: 150-200 píxeles
        # Umbral anterior (15px): 97.6% falsos positivos (41/42)
        # Umbral 100px: Rechazaba supplies pequeños válidos (78px)
        # Nuevo umbral: 70 píxeles = captura todos los reales (10/11 = 90.9%)
        min_pixels = 70
        
        # v3.4.8.7: Filtrado removido - ahora se hace en main.py de forma centralizada
        for label in range(1, labels.max()+1):
            rows, cols = np.where(labels == label)
            if len(rows) > min_pixels:
                center_y = self.shooting_zone[0] + int(np.mean(rows))
                center_x = self.shooting_zone[2] + int(np.mean(cols))
                pos.append([center_y, center_x])
                self.logger.debug(f"   ✅ Supply drop #{label}: {len(rows)} píxeles en posición ({center_y}, {center_x})")
        
        # 📸 CAPTURA DEBUG: Guardar imagen con detecciones marcadas
        if len(pos) > 0:
            self._save_detection_screenshot(background, pos, "supply", self.supply_counter)
            self.logger.info(f"🟠 [SUPPLY DROP] Detectados {len(pos)} supply drops: {pos}")
        else:
            self.logger.debug("   ❌ No se detectaron supply drops")
        
        return pos

    def detect_coins(self, background):
        """Detects coin chests, but there might be false positives"""
        if keyboard.is_pressed("q"):
            raise KeyboardInterrupt

        pos = []

        # threshold + clean up
        background_cropped = background[self.shooting_zone[0]:self.shooting_zone[1],
                                        self.shooting_zone[2]:self.shooting_zone[3]]
        mask = (background_cropped[:,:,0] >= self.coin_color[0]) * \
                (background_cropped[:,:,1] >= self.coin_color[1]) * \
                (background_cropped[:,:,2] >= self.coin_color[2]) * \
                (background_cropped[:,:,0] <= self.coin_color[3]) * \
                (background_cropped[:,:,1] <= self.coin_color[4]) * \
                (background_cropped[:,:,2] <= self.coin_color[5])
        mask = morphology.binary_opening(mask, np.ones((3,3)))
        mask = morphology.binary_closing(mask, np.ones((5,5)))
        # connected components
        labels = measure.label(mask, background=0, connectivity=2)

        # find center of mass - REDUCIDO DE 15 A 10
        for label in range(1, labels.max()+1):
            rows, cols = np.where(labels == label)
            if len(rows) > 10:  # Cambiado de 15 a 10
                pos.append([self.shooting_zone[0] + int(np.mean(rows)), self.shooting_zone[2] + int(np.mean(cols))])

        # 📸 CAPTURA DEBUG: Guardar imagen con detecciones marcadas
        if len(pos) > 0:
            self._save_detection_screenshot(background, pos, "coin", self.coin_counter)
            print(f"[COINS] Detectadas {len(pos)} monedas")
        
        return pos

    # def detect_coins(self, background):
    #     """Detects coin chests, but there might be false positives"""
    #     if keyboard.is_pressed("q"):
    #         raise KeyboardInterrupt

    #     pos = []
    #     background_cropped = background[self.shooting_zone[0]:self.shooting_zone[1],
    #                                     self.shooting_zone[2]:self.shooting_zone[3]]
    #     background_cropped_gray = color.rgb2gray(background_cropped)
    #     # import matplotlib.pyplot as plt

    #     pos = []
    #     corr = np.zeros_like(background_cropped_gray)
    #     for template in self.coin_chests:
    #         # for ang in [0, 90, 180, 270]:
    #             # template_gray = color.rgb2gray(transform.rotate(template, ang))
    #         template_gray = color.rgb2gray(template)
    #         # result = feature.match_template(feature.canny(background_cropped_gray, sigma=2), 
    #         #                                 feature.canny(template_gray, sigma=2), mode="reflect")
    #         result = feature.match_template(filters.sobel(background_cropped_gray), 
    #                                         filters.sobel(template_gray), pad_input=True, mode="reflect")
    #         corr += transform.resize(result, corr.shape, anti_aliasing=True)
    #         # corr += feature.match_template(filters.sobel(background_cropped_gray), 
    #         #                                 filters.sobel(template_gray), pad_input=True, mode="reflect")
    #     corr = corr / len(self.coin_chests)
    #     coordinates = feature.peak_local_max(corr, min_distance=50, threshold_abs=0.1)
    #     import matplotlib.pyplot as plt
    #     plt.figure(2)
    #     plt.imshow(corr, vmax=1, vmin=-1)
    #     plt.figure(3)
    #     plt.imshow(background_cropped)
    #     plt.plot(coordinates[:, 1], coordinates[:, 0], 'r.')
    #     plt.figure(4)
    #     plt.imshow(filters.sobel(template_gray))
    #     plt.show()

    #     # # find center of mass
    #     # for label in range(1, labels.max()+1):
    #     #     rows, cols = np.where(labels == label)
    #     #     if len(rows) > 15:
    #     #         pos.append([self.shooting_zone[0] + int(np.mean(rows)), self.shooting_zone[2] + int(np.mean(cols))])

    #     return pos

    def detect_dino(self, background):
        """Finds the location of dino but there are false positives need more cleaning"""

        pos = []

        # convert background gray
        background_cropped = background[self.shooting_zone[0]:self.shooting_zone[1],
                                        self.shooting_zone[2]:self.shooting_zone[3]]

        edges = filters.sobel(background_cropped)

        mask = (edges[:,:,0] <= 0.089) * \
                (edges[:,:,1] <= 0.089) * \
                (edges[:,:,2] <= 0.089) 
        mask = filters.median(mask, np.ones((3, 3)))
        mask = morphology.binary_closing(mask, np.ones((5, 5)))
        
        # connected components
        labels = measure.label(mask, background=0, connectivity=2)
        dist = ndimage.distance_transform_edt(mask)
        
        # Extract region properties for filtering
        regions = measure.regionprops(labels)
        
        # Filtros optimizados para reducir falsos positivos (v3.4.8.9.7)
        # Análisis con 6 dinos reales confirmados: reduce 114 → 31 detecciones (72.8%)
        MIN_AREA = 31      # Mínimo: dinos pequeños (63px) con margen
        MAX_AREA = 6321    # Máximo: dinos grandes (2107px) x3 para raids
        MIN_RATIO = 0.30   # Aspect ratio mínimo (ancho/alto)
        MAX_RATIO = 1.97   # Aspect ratio máximo

        # find center of mass with filters
        for region in regions:
            # Calcular características
            area = region.area
            bbox = region.bbox  # (min_row, min_col, max_row, max_col)
            height = bbox[2] - bbox[0]
            width = bbox[3] - bbox[1]
            aspect_ratio = width / height if height > 0 else 0
            
            # Aplicar filtros de área y forma
            if not (MIN_AREA <= area <= MAX_AREA):
                continue  # Área fuera de rango
            if not (MIN_RATIO <= aspect_ratio <= MAX_RATIO):
                continue  # Forma incorrecta (muy alargado o muy plano)
            
            # Calcular centro usando distance transform
            label_dist = dist * (labels == region.label).astype(np.uint8)
            row, col = np.unravel_index(label_dist.argmax(), label_dist.shape)
            pos.append([self.shooting_zone[0] + row, 
                        self.shooting_zone[2] + col])

        # 📸 CAPTURA DEBUG: Guardar imagen con detecciones marcadas
        if len(pos) > 0:
            self._save_detection_screenshot(background, pos, "dino", self.dino_counter)

        # import matplotlib.pyplot as plt
        # plt.figure(1)
        # plt.imshow(dist)
        # plt.figure(4)
        # plt.imshow(labels)
        # plt.figure(5)
        # plt.imshow(mask)        

        # plt.figure(2)
        # plt.imshow(edges)
        
        # plt.show()
        return pos  

    # ----------------------------------------------------------
    #   OCR
    # ----------------------------------------------------------

    def determine_dino_collected(self, background):
        if keyboard.is_pressed("q"):
            raise KeyboardInterrupt

        type_text = background[self.dino_collected_text_loc[0]:self.dino_collected_text_loc[1], 
                                self.dino_collected_text_loc[2]:self.dino_collected_text_loc[3]].astype(np.uint8)
        
        amount_text = background[self.dino_collected_amount_loc[0]:self.dino_collected_amount_loc[1],
                                self.dino_collected_amount_loc[2]:self.dino_collected_amount_loc[3]]

        config = '--oem 1 --psm 4'
        key = pytesseract.image_to_string(type_text).split() # "".join(pytesseract.image_to_string(type_text).split()) # , config = self.custom_config).split())
        number = "".join(pytesseract.image_to_string(amount_text, config = config).split())

        print(key, number) 

    def determine_supply_collected(self, background):
        """"Determines which supply collected and how much"""

        if keyboard.is_pressed("q"):
            raise KeyboardInterrupt

        type_text = background[self.supply_drop_resources_text_loc[0]:self.supply_drop_resources_text_loc[1], 
                                self.supply_drop_resources_text_loc[2]:self.supply_drop_resources_text_loc[3]].astype(np.uint8)
        
        amount_text = background[self.supply_drop_resources_amount_loc[0]:self.supply_drop_resources_amount_loc[1],
                                self.supply_drop_resources_amount_loc[2]:self.supply_drop_resources_amount_loc[3]]

        key = "".join(pytesseract.image_to_string(type_text).split()) # , config = self.custom_config).split())
        number = "".join(pytesseract.image_to_string(amount_text).split()) #, config = self.custom_config).split())

        print(key, number) 
        # don't think about the case when it fails right now  

        try:
            number = int(number[1:])
        except ValueError:
            number = None

        if key and number:
            return key, number


    def filter_excluded_zones(self, positions, object_type):
        """Filtra posiciones que están en zonas prohibidas (UI elements)
        
        Args:
            positions: Lista de [y, x] posiciones detectadas
            object_type: Tipo de objeto ("coin", "supply", "dino") para logging
            
        Returns:
            Lista filtrada de posiciones válidas
        """
        # v3.4.8.9.6: ZONAS EXCLUIDAS AJUSTADAS - Bordes más estrechos
        # Basado en pruebas: bordes de 50px bloqueaban supplies válidos
        # Nuevos bordes: 20px (izq) y 540px (der) solo bloquean UI extrema
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
        
        valid_positions = []
        for pos in positions:
            y, x = pos[0], pos[1]
            is_excluded = False
            
            for zone in excluded_zones:
                if (zone['x_min'] <= x <= zone['x_max'] and 
                    zone['y_min'] <= y <= zone['y_max']):
                    self.logger.debug(f"⛔ [{object_type.upper()}] Posición ({y}, {x}) en zona excluida: {zone['name']}")
                    is_excluded = True
                    break
            
            if not is_excluded:
                valid_positions.append(pos)
        
        return valid_positions
            

    def determine_state(self, background):
        """After you click determine is this supply drop/dino/coin chase etc."""

        if keyboard.is_pressed("q"):
            raise KeyboardInterrupt

        state = ""
        
        # 🛡️ v3.4.7: FALLBACK DESACTIVADO - Causa falsos positivos con supply drops
        # Los supply drops también tienen X, no se debe clickear automáticamente
        # La X se clickea SOLO cuando OCR confirma que NO es supply/event
        # pos_x = self.locate_x_button(background)
        # if pos_x:
        #     self.logger.warning("⚠️  [FALLBACK] Detectada X de salida - Clickeando para salir de pantalla problemática")
        #     pyautogui.click(x=self.x+pos_x[1], y=self.y+pos_x[0])
        #     time.sleep(1)
        #     state = "out_of_range"
        #     return state
        
        self.logger.debug("🔍 Determinando estado del objeto...")
        
        # Capturar áreas para detección
        launch_button = background[self.launch_button_loc[0]:self.launch_button_loc[1], 
                                self.launch_button_loc[2]:self.launch_button_loc[3]].astype(np.uint8)
        
        supply_drop = background[self.supply_drop_text_loc[0]:self.supply_drop_text_loc[1],
                                self.supply_drop_text_loc[2]:self.supply_drop_text_loc[3]]
        
        # ⏱️ v3.4.3: Área SEPARADA solo para cooldown (no interfiere con launch button)
        cooldown_area = background[self.cooldown_text_loc[0]:self.cooldown_text_loc[1],
                                   self.cooldown_text_loc[2]:self.cooldown_text_loc[3]]

        self.logger.debug(f"   📐 Área botón lanzar: {launch_button.shape}")
        self.logger.debug(f"   📐 Área texto supply: {supply_drop.shape}")
        self.logger.debug(f"   📐 Área cooldown: {cooldown_area.shape}")

        # Intentar OCR en las zonas principales
        text1 = "".join(pytesseract.image_to_string(launch_button, config = self.custom_config).split()).upper()
        text2 = "".join(pytesseract.image_to_string(supply_drop, config = self.custom_config).split()).upper()
        
        # OCR en área de cooldown (separado para no contaminar detección principal)
        cooldown_text = "".join(pytesseract.image_to_string(cooldown_area, config = self.custom_config).split()).upper()
        
        # Combinar textos PRINCIPALES (sin cooldown para no interferir)
        combined_text = text1 + " " + text2

        self.logger.info(f"📝 [OCR] Botón: '{text1}'")
        self.logger.info(f"📝 [OCR] Texto: '{text2}'")
        self.logger.info(f"📝 [OCR] Combinado: '{combined_text}'")
        if cooldown_text:
            self.logger.debug(f"⏱️  [OCR] Cooldown: '{cooldown_text}'")
        
        # ⛔ FILTRO DE EXCLUSIÓN: Detectar objetos que NO debemos clickear
        
        # 1. Dinosaurios fuera de rango (VIP requerido)
        if any(word in combined_text for word in ["UNETE", "ÚNETE", "AHORA", "JOINNOW", "JOIN"]):
            state = "out_of_range"
            self.logger.warning("⛔ [EXCLUIDO] Dinosaurio fuera de rango (VIP requerido)")
            return state
        
        # 2. Páginas de compra/bonificación
        if any(word in combined_text for word in ["COMPRA", "COMPRAR", "BUY", "PURCHASE", "BONIFICACION", "BONIFICACIÓN", "OFERTA", "OFFER", "PRECIO", "PRICE", "$", "USD", "PAQUETE", "PACK"]):
            state = "out_of_range"
            self.logger.warning("⛔ [EXCLUIDO] Página de compra/oferta detectada")
            return state
        
        # 3. Pantallas de carga o menús que no son interactivos
        if any(word in combined_text for word in ["CARGANDO", "LOADING", "ESPERA", "WAIT", "MENU", "MENÚ"]):
            state = "out_of_range"
            self.logger.warning("⛔ [EXCLUIDO] Pantalla de carga o menú")
            return state
        
        # 4. ✅ SUPPLY DROPS LEGÍTIMOS - VERIFICAR PRIMERO antes de rechazar por "ASALTO"/"EVENTO"
        # CRÍTICO: Algunos supply drops dicen "ACTUALIZACIÓN DE SUMINISTRO" o "EVENTO ESPECIAL"
        # Si el OCR lee mal "EVENTO DE ASALTO" pero también detecta "SUMINISTRO", es un supply legítimo
        if any(word in combined_text for word in ["SUMINISTRO", "SUMINISTROS", "SUPPLY", "DROP", "ABASTECIMIENTO"]):
            state = "supply"
            self.logger.debug("   📦 Palabras clave de SUPPLY detectadas (prioridad alta)")
            return state
        
        # 5. 🚫 INCUBADORAS - Eventos de combate/asalto (DESPUÉS de verificar supply)
        # Solo rechazar si tiene "ASALTO"/"COMBATE" pero NO tiene "SUMINISTRO"
        if any(word in combined_text for word in ["COMBATE", "BATTLE", "ASALTO", "INCUBADORA", "INCUBATOR"]):
            state = "out_of_range"
            self.logger.warning("⛔ [EXCLUIDO] Incubadora o evento de combate detectado")
            return state
        
        # 6. 🏛️ RAIDS - Detectan "JEFE" o "NIVEL" en el texto
        if "JEFE" in combined_text or "BOSS" in combined_text or "NIVEL" in combined_text or "LEVEL" in combined_text or "RECOMPENSAS" in combined_text or "REWARDS" in combined_text:
            state = "out_of_range"
            self.logger.warning("⛔ [EXCLUIDO] Raid con jefe detectado")
            return state
        
        # 7. 🛕 SANTUARIOS - Botón dice "ENTRAR" o texto dice "SANTUARIO"
        # OCR puede leer mal "ENTRAR" como "FNTRAR", "FMTRAR", etc.
        if ("ENTRAR" in text1 or "ENTER" in text1 or "NTRAR" in text1 or "TRAR" in text1) or "SANTUARIO" in combined_text or "SANCTUARY" in combined_text:
            state = "out_of_range"
            self.logger.warning("⛔ [EXCLUIDO] Santuario detectado")
            return state
        
        # 8. ⏱️ SUPPLY DROPS EN COOLDOWN - Ya fueron recolectados recientemente
        # v3.4.3: Usa área SEPARADA dedicada solo a cooldown, no contamina el OCR principal
        # Detecta tiempo restante en formato: "0m 9s", "14h 10m", "1h", "30m", etc.
        import re
        cooldown_patterns = [
            r'\d+[HMS]',        # Formato simple: "1H", "30M", "45S"
            r'\d+[hms]',        # Formato minúsculas: "1h", "30m", "45s"  
            r'\d+[HMS]\s*\d*[HMS]?',  # Formato compuesto: "14H 10M", "1H 30M"
            r'\d+[hms]\s*\d*[hms]?',  # Formato compuesto minúsculas: "0m 9s", "14h 10m"
        ]
        
        # Buscar cooldown SOLO en el área dedicada (no en combined_text)
        has_cooldown_time = any(re.search(pattern, cooldown_text) for pattern in cooldown_patterns)
        
        if has_cooldown_time:
            state = "out_of_range"
            self.logger.warning(f"⛔ [EXCLUIDO] Supply drop en cooldown - Tiempo: '{cooldown_text[:30]}'")
            return state
        
        # ✅ EVENTOS ESPECIALES SON VÁLIDOS - NO se excluyen
        # Los supply drops que dicen "EVENTO ESPECIAL TERMINA EN..." SON cajitas verdes con suministros
        # Los dinosaurios de evento también son válidos para disparar y recolectar ADN
        
        # MEJORADO: Buscar en TEXTO COMBINADO para más robustez
        # Prioridad: SUPPLY > COIN > DINO (supply primero para evitar falsos positivos con "LANZAR")
        # NOTA: SUPPLY ya se verificó arriba (líneas 757-760) con prioridad alta
        
        # 1. Detectar EVENTOS VERDES (cajitas de evento especial) - Ahora separado de supply drops normales
        # Estos pueden decir "EVENTO ESPECIAL TERMINA EN..." y son legítimos
        if any(word in combined_text for word in ["EVENTO", "EVENT", "ESPECIAL", "SPECIAL"]) and state != "supply":
            state = "event"
            self.logger.debug("   � Evento especial detectado")
            
        # 2. Detectar MONEDAS / COIN CHASE
        elif any(word in combined_text for word in ["MONEDA", "MONEDAS", "COIN", "CHASE", "ORO", "GOLD", "PERSECUCION", "PERSECUCIÓN"]):
            state = "coin"
            self.logger.debug("   🪙 Palabras clave de COIN detectadas")
        
        # 3. Detectar DINOSAURIOS (al final para evitar falsos positivos)
        # "LANZAR" puede aparecer en supply drops, así que verificamos esto último
        elif any(word in combined_text for word in ["LANZAR", "DISPARAR", "LAUNCH", "SHOOT", "CAPTURAR", "CAPTURA"]):
            state = "dino"
            self.logger.debug("   🦖 Palabras clave de DINO detectadas")
        
        # 4. Detección por fragmentos parciales (fallback)
        elif any(fragment in combined_text for fragment in ["SUMIN", "DINO", "MONED"]):
            if "SUMIN" in combined_text:
                state = "supply"
                self.logger.debug("   📦 Fragmento 'SUMIN' detectado")
            elif "MONED" in combined_text:
                state = "coin"
                self.logger.debug("   🪙 Fragmento 'MONED' detectado")
            elif "DINO" in combined_text:
                state = "dino"
                self.logger.debug("   🦖 Fragmento 'DINO' detectado")
            elif "MONED" in combined_text:
                state = "coin"
                self.logger.debug("   🪙 Fragmento 'MONED' detectado")

        if state:
            self.logger.info(f"✅ [ESTADO DETECTADO] {state.upper()}")
        else:
            self.logger.warning(f"❌ [ESTADO DETECTADO] NO IDENTIFICADO - OCR puede haber fallado")
            self.logger.warning(f"   💡 Considera activar debug visual para ver qué captura el OCR")

        return state

    # ----------------------------------------------------------
    #   CHANGE LOCATION
    # ----------------------------------------------------------

    def change_location(self, r=300):
        """Randomly change location"""

        if keyboard.is_pressed("q"):
            raise KeyboardInterrupt

        time.sleep(1)

        # press ctrl + shift + k to open the map
        pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2)
        time.sleep(0.5)

        pyautogui.keyDown('ctrl') 
        time.sleep(0.1)

        pyautogui.keyDown('shift') 
        time.sleep(0.1)

        pyautogui.press('k')
        time.sleep(0.1)

        pyautogui.keyUp('ctrl')
        pyautogui.keyUp('shift')
        time.sleep(2) 

        
        # detect current location
        background = np.array(pyautogui.screenshot())
        mask = (background[:,:,0] >= self.gmap_loc_color[0]) * \
                (background[:,:,1] >= self.gmap_loc_color[1]) * \
                (background[:,:,2] >= self.gmap_loc_color[2]) * \
                (background[:,:,0] <= self.gmap_loc_color[3]) * \
                (background[:,:,1] <= self.gmap_loc_color[4]) * \
                (background[:,:,2] <= self.gmap_loc_color[5])
        labels = measure.label(mask)
        mask = labels == np.argmax(np.bincount(labels[labels != 0].flatten()))
        
        # move randomly
        if np.sum(mask) > 0:
            y_, x_ = np.where(mask)
            pos = (y_.mean(), x_.mean())
            
            ang = np.random.uniform(0, 2*np.pi)
            dx = r*np.cos(ang)
            dy = r*np.sin(ang)

            pyautogui.click(x=pos[1] + dx, y=pos[0] + dy)
            time.sleep(2) 
        else:
            raise KeyboardInterrupt("Cannot find google map location")

        # press ctrl + shift + 2 to go back to game
        pyautogui.keyDown('ctrl') 
        time.sleep(0.1)

        pyautogui.keyDown('shift') 
        time.sleep(0.1)

        pyautogui.press('2')
        time.sleep(0.1)

        pyautogui.keyUp('ctrl')
        pyautogui.keyUp('shift')
        time.sleep(25)
        # time.sleep(7.5)

        # click launch button incase we move so far
        background = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
        if self.moved_too_far(background):
            print("--"*10)
            print("MOVED TO FAR")
            pos = ((self.launch_button_loc[1] + self.launch_button_loc[0])/2, 
                   (self.launch_button_loc[3] + self.launch_button_loc[2])/2)
            pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
            time.sleep(1)

    def change_view(self):
        """"Rotates the screen after everthing is collected"""
        print("--"*10)
        print("CHANGING VIEW")
        
        # 📸 CAPTURA DE ANÁLISIS: Guardar pantalla antes de rotar para analizar detecciones
        background_before = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
        timestamp = datetime.now().strftime("%H%M%S")
        
        try:
            from PIL import Image
            debug_folder = "debug_screenshots"
            if not os.path.exists(debug_folder):
                os.makedirs(debug_folder)
            Image.fromarray(background_before).save(f"{debug_folder}/map_view_{timestamp}.png")
            self.logger.debug(f"📸 Captura guardada: map_view_{timestamp}.png")
        except Exception as e:
            self.logger.debug(f"⚠️  Error al guardar captura: {e}")
        
        pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2)
        time.sleep(1)

        background = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
        pos = self.locate_x_button(background)
        if pos:
            pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
            time.sleep(1)  

        pyautogui.moveTo(self.x+self.w//2, self.y+self.h//2, 0.1)
        pyautogui.scroll(90)
        time.sleep(1)

    def moved_too_far(self, background):
        """"Detects when we move to far."""
        background = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
        color = background[self.moved_too_far_loc[0], 
                           self.moved_too_far_loc[1], :]
        # print(color)
        if 120 > color[0] > 100 and \
           10 > color[1] > 0 and \
           10 > color[2] > 0:
           return True
        return False

        # img = self.moved_too_far_pic.resize((self.w, self.h), Image.ANTIALIAS)
        # moved_too_far_resized = np.array(img)[:, :, :3]
        # print("DIST", np.mean((moved_too_far_resized.astype(np.float) - background.astype(np.float))**2))
        # return not self.background_changed(moved_too_far_resized, background, 2000)

    # ----------------------------------------------------------
    #   DINO COLLECTION
    # ----------------------------------------------------------

    def is_dino_loading_screen(self, background):
        
        img = self.loading_screen_pic.resize((self.w, self.h), Image.ANTIALIAS)

        # some reason image become 4D 
        loading_screen_resized = np.array(img)[:, :, :3]
        return not self.background_changed(loading_screen_resized, background)


    def get_battery_left(self, background):
        """Returns how much battery left, betwen [0 (full), 1 (empty)]"""
        # crop battery
        battery = background[self.battery_loc[0]:self.battery_loc[1],
                             self.battery_loc[2]:self.battery_loc[3]]

        # get length
        mask = (battery[:,:,0] <= self.battery_color[0]) * \
                (battery[:,:,1] <= self.battery_color[1]) * \
                (battery[:,:,2] <= self.battery_color[2])
        line_length = 0
        if np.sum(mask) > 0:
            _, cols = np.where(mask)
            line_length = cols.max() - cols.min()

        # normalize as percentage - CORREGIDO: Retorna batería RESTANTE (0=vacía, 1=llena)
        battery_remaining = 1.0 - (line_length / abs(self.battery_loc[3] - self.battery_loc[2]))
        return battery_remaining

    def shoot_dino(self):
        """Shoots the dino"""

        def dino_location(background, shift, D):
            """Find the critical point"""
            pos = []
            D_ = D


            mask = (background[:,:,0] >= 180) * \
                   (background[:,:,1] >= 180) * \
                   (background[:,:,2] >= 180)  

            mask = filters.median(mask, np.ones((3, 3)))
            mask = morphology.binary_opening(mask, np.ones((1, 5)))
            mask = morphology.binary_opening(mask, np.ones((5, 1)))

            dist = ndimage.distance_transform_edt(mask)
            if np.sum(mask) > 0:
                # labels = measure.label(mask)
                rows, cols = np.where(dist >= np.max(dist))
                pos = [shift + np.mean(rows), np.mean(cols)]
                D_ =  np.max(dist) if np.max(dist) - 5 > 0 else D
                # import matplotlib.pyplot as plt
                # plt.figure(1)
                # plt.imshow(mask)
                # plt.figure(2)
                # plt.imshow(dist)
                # plt.show()
            return pos, D_
        
        # hyper parameters
        D = 2*self.D
        v_max = self.v_max * 2.0  # ⚡ v3.4.6: AUMENTADO de 1.5x a 2.0x para seguir dinos más rápido
        S = 4
        ms = 0.02  # ⚡ v3.4.6: REDUCIDO de 0.05 a 0.02 = mouse más rápido
        h1, h2, h3 = 5, 2, 2, # 10, 2, 2
        
        # detect dart location 
        dart_loc = self.dart_loc 
        prev_dino_loc = None
        vel = [0, 0]
        buffer = 10
        

        cx = (self.launch_button_loc[2] + self.launch_button_loc[3]) / 2
        cy = (self.launch_button_loc[0] + self.launch_button_loc[1]) / 2
        pyautogui.moveTo(self.x+cx, self.y+cy, 0.5)  # ⚡ REDUCIDO de 1 a 0.5 segundos
        pyautogui.mouseDown()
        time.sleep(0.3)  # ⚡ REDUCIDO de 0.5 a 0.3 segundos
        
        background = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))

        start = time.time()
        end = start
        shots_attempted = 0
        last_shot_attempt = start
        
        # 🎯 v3.4.8.9.0: SISTEMA HÍBRIDO DE 2 FASES
        # FASE 1: Intento rápido de centrado (5s)
        # FASE 2: Disparo rápido garantizado si no centró
        phase_1_duration = 5  # Intentar trackear por 5 segundos
        phase_1_end = start + phase_1_duration
        successfully_centered = False

        # ========== FASE 1: INTENTO DE CENTRADO RÁPIDO ==========
        self.logger.info("🎯 [FASE 1] Intentando centrar dino (5s)...")
        
        while not self.is_dino_loading_screen(background) and end < phase_1_end:
            
            if keyboard.is_pressed("q"):
                raise KeyboardInterrupt

            background = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
            background_cropped = background[self.dino_shoot_loc[0]:,:self.dino_shoot_loc[1],:]
            dino_loc, _ = dino_location(background_cropped, self.dino_shoot_loc[0], 2*self.D)
            
            end = time.time()

            if not dino_loc and prev_dino_loc:
                # ⚡ MEJORADO: Predicción más agresiva cuando no se detecta el dino
                dino_loc = [prev_dino_loc[0] + vel[0] * 2,  # Multiplicado por 2 para seguir mejor el movimiento
                            prev_dino_loc[1] + vel[1] * 2]
   
            if dino_loc:
                dino_2_dart = np.sqrt((dino_loc[0] - dart_loc[0])**2 + (dino_loc[1] - dart_loc[1])**2)
                battery_left = self.get_battery_left(background)  # CORREGIDO: Ya no se invierte

                # check if dino in dart range - v3.4.6: Rango ampliado 1.5x para disparar más fácil
                shoot_range = (D + h1*battery_left) * 1.5
                if dino_2_dart <= shoot_range:
                    print("--"*10)
                    print("DINO CLOSE SHOOTING")
                    pyautogui.mouseUp()
                    time.sleep(0.1)  # ⚡ v3.4.8: REDUCIDO de 0.25s a 0.1s
                    pyautogui.mouseDown()
                    time.sleep(0.3)  # ⚡ v3.4.8: REDUCIDO de 0.5s a 0.3s
                    # 🚀 v3.4.8: CONTINUAR inmediatamente para perseguir
                    continue
                else: # if not move screen to dino
                    v_max_new = v_max + h2*battery_left

                    # ⚡ v3.4.8: Factor de predicción AUMENTADO para dinos ultra-rápidos
                    # 3x → 5x → 7x para anticipar mejor el movimiento
                    prediction_factor = 7.0
                    dino_loc_pred = [dino_loc[0] + vel[0] * prediction_factor * (dino_2_dart / v_max_new),  
                                    dino_loc[1] + vel[1] * prediction_factor * (dino_2_dart / v_max_new)] 

                    # get direction and multiply with v_max
                    dino_pred_2_dart = np.sqrt((dino_loc_pred[0] - dart_loc[0])**2 + (dino_loc_pred[1] - dart_loc[1])**2)
                    x_v =  v_max_new * (dino_loc_pred[1] - dart_loc[1]) / dino_pred_2_dart
                    y_v =  v_max_new * (dino_loc_pred[0] - dart_loc[0]) / dino_pred_2_dart

                    # if we are to close move slower
                    slow_down_speed = min(1, (dino_2_dart/((S - h3*battery_left)*D)))
                    mouse_pos = pyautogui.position()

                    # don't go outside the screen
                    dx = min(max(mouse_pos[0] + x_v*slow_down_speed, self.x + buffer), self.x + self.w - 4*buffer)
                    dy = min(max(mouse_pos[1] + y_v*slow_down_speed, self.y + buffer), self.y + self.h - buffer)

                    pyautogui.moveTo(dx, dy, ms)
                
                if prev_dino_loc:
                    vel = [dino_loc[0] - prev_dino_loc[0], dino_loc[1] - prev_dino_loc[1]]
                prev_dino_loc = dino_loc

            else:
                # shoot to reset the dart circle
                pyautogui.mouseUp()
                time.sleep(0.5)
                pyautogui.moveTo(self.x+cx, self.y+cy, 0.1)  
                pyautogui.mouseDown() 
            # print("DIST", np.mean((b_prev.astype(np.float) - background.astype(np.float))**2))
        
        # ========== VERIFICAR SI FASE 1 TUVO ÉXITO ==========
        if self.is_dino_loading_screen(background):
            successfully_centered = True
            self.logger.info("✅ [FASE 1] Dino centrado correctamente - Pantalla de carga detectada")
        else:
            self.logger.warning("⚠️  [FASE 1] No se centró en 5s - Pasando a FASE 2...")
            
            # ========== FASE 2: DISPARO RÁPIDO GARANTIZADO ==========
            self.logger.info("🎯 [FASE 2] Disparos rápidos en patrón (garantiza dardos para alianza)")
            
            # Soltar mouse antes de disparar
            pyautogui.mouseUp()
            time.sleep(0.3)
            
            # Patrón de disparo: 4 posiciones estratégicas para maximizar cobertura
            shoot_positions = [
                (self.w//2, self.h//2),              # Centro
                (self.w//2 + 80, self.h//2 - 60),    # Arriba-derecha
                (self.w//2 - 80, self.h//2 + 60),    # Abajo-izquierda  
                (self.w//2, self.h//2 + 40),         # Centro-abajo
            ]
            
            for i, (offset_x, offset_y) in enumerate(shoot_positions, 1):
                self.logger.debug(f"   💉 Disparo rápido {i}/4...")
                
                # Mover a posición
                pyautogui.moveTo(self.x + offset_x, self.y + offset_y, 0.1)
                
                # Disparar (press + hold + release)
                pyautogui.mouseDown()
                time.sleep(0.4)  # Hold brevemente
                pyautogui.mouseUp()
                time.sleep(0.3)  # Pausa entre disparos
                
                # Verificar si ya disparó todo (detectó loading screen)
                background = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
                if self.is_dino_loading_screen(background):
                    self.logger.info(f"✅ [FASE 2] Dardos agotados después de {i} disparos")
                    successfully_centered = True  # Marcamos como exitoso
                    break
            
            self.logger.info("✅ [FASE 2] Disparos completados")
        
        # ========== FINALIZACIÓN ==========
        # Ya no necesitamos el bloque de "Si salió sin disparar"
        # porque FASE 2 garantiza que siempre se disparan dardos
        
        if end - start > 120:  # CORREGIDO: Cambiado de 60 a 120
            pyautogui.mouseUp()
            time.sleep(0.25)
            pyautogui.mouseDown()
            time.sleep(60)  

            pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2) 
            time.sleep(1)           

        else:
            print("--"*10)
            print("DONE")
            while self.is_dino_loading_screen(background):
                background = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
                time.sleep(1)
            time.sleep(20) 
            # read how much and which dino we shoot it
            
            pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2) 
            time.sleep(5) 

    def collect_dino(self, filtered_positions=None):
        """"Finds and shoots the dino
        
        Args:
            filtered_positions: Lista pre-filtrada de posiciones [y, x]. 
                               Si es None, detecta normalmente.
        """
        
        background = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
        dino_pos = filtered_positions if filtered_positions is not None else self.detect_dino(background)
        
        # Incrementar contador para siguiente detección
        self.dino_counter += 1
        
        print("--"*10)
        print("TOTAL NUMBER OF DINO", len(dino_pos))
        for i, pos in enumerate(dino_pos):
            if keyboard.is_pressed("q"):
                raise KeyboardInterrupt

            background_old = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
            pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
            time.sleep(0.02)
            background_new = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))

            # to many FPs so quick way to eliminate them
            if not self.background_changed(background_old, background_new):
                print("--"*10)
                print("NOTHING THERE")
                continue

            time.sleep(0.8)
            background_new = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
            state = self.determine_state(background_new)

            # 🔧 FIX: Si detectamos supply/coin en vez de dino, recolectarlo apropiadamente
            if state == "supply" or state == "event":
                self.logger.info(f"🎁 Detectado {state.upper()} en loop de dinos - Recolectando como supply...")
                pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2)
                time.sleep(2.5)
                for i in range(3):
                    pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2)
                    time.sleep(1.5)
                background_after = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
                if self.background_changed(background_new, background_after):
                    pos_x = self.locate_x_button(background_after)
                    if pos_x:
                        pyautogui.click(x=self.x+pos_x[1], y=self.y+pos_x[0])
                    else:
                        pyautogui.click(x=self.x+self.map_button_loc[1], y=self.y+self.map_button_loc[0])
                    time.sleep(1)
                self.logger.info(f"✅ {state.upper()} recolectado desde loop de dinos")
                
            elif state == "coin":
                self.logger.info("🪙 Detectada COIN en loop de dinos - Recolectando...")
                pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2)
                time.sleep(2.5)
                pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2)
                background_after = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
                if self.background_changed(background_new, background_after):
                    pos_x = self.locate_x_button(background_after)
                    if pos_x:
                        pyautogui.click(x=self.x+pos_x[1], y=self.y+pos_x[0])
                    else:
                        pyautogui.click(x=self.x+self.map_button_loc[1], y=self.y+self.map_button_loc[0])
                    time.sleep(1)
                self.logger.info("✅ COIN recolectada desde loop de dinos")
                
            elif state == "dino":
                cx = (self.launch_button_loc[2] + self.launch_button_loc[3]) / 2
                cy = (self.launch_button_loc[0] + self.launch_button_loc[1]) / 2
                pyautogui.click(x=self.x+cx, y=self.y+cy)  
                time.sleep(0.5)

                background_loading_screen = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
                while self.is_dino_loading_screen(background_loading_screen):
                    background_loading_screen = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
                    time.sleep(1)

                print("--"*10)
                print("TIME TO SHOOT")                
                
                time.sleep(0.3)
                self.shoot_dino()

                # there is some bug in JW which is expected when I shoot a dino it turn to original direction
                for _ in range(self.number_of_scrolls):
                    self.change_view()

            else:
                print("--"*10)
                print("NOT DINO")
                pos = self.locate_x_button(background_new)
                pos = pos if pos else self.map_button_loc
                pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
                time.sleep(1)  

    # ----------------------------------------------------------
    #   COIN COLLECTION
    # ----------------------------------------------------------

    def collect_coin(self, filtered_positions=None):
        """Collects coin chests
        
        Args:
            filtered_positions: Lista pre-filtrada de posiciones [y, x]. 
                               Si es None, detecta normalmente.
        """
        background = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
        coin_pos = filtered_positions if filtered_positions is not None else self.detect_coins(background)

        # Incrementar contador para siguiente detección
        self.coin_counter += 1

        for pos in coin_pos:
            if keyboard.is_pressed("q"):
                raise KeyboardInterrupt

            if np.sqrt((pos[0] - self.center_loc[0])**2 + (pos[1] - self.center_loc[1])**2) < 30:
                continue

            background_old = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
            pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
            time.sleep(0.2)
            background_new = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))

            # to many FPs so quick way to eliminate them
            if not self.background_changed(background_old, background_new):
                print("--"*10)
                print("NOTHING THERE")
                continue

            time.sleep(0.8)
            background_new = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
            state = self.determine_state(background_new)
            
            # 🔧 FIX: Si detectamos supply en vez de coin, recolectarlo como supply
            # Esto pasa porque los rangos de color se solapan
            if state == "supply" or state == "event":
                self.logger.info(f"🎁 Detectado {state.upper()} en loop de coins - Recolectando como supply...")
                pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2)
                time.sleep(2.5)
                for i in range(3):
                    pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2)
                    time.sleep(1.5)
                # Cerrar si quedó abierto
                background_after = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
                if self.background_changed(background_new, background_after):
                    pos_x = self.locate_x_button(background_after)
                    if pos_x:
                        pyautogui.click(x=self.x+pos_x[1], y=self.y+pos_x[0])
                    else:
                        pyautogui.click(x=self.x+self.map_button_loc[1], y=self.y+self.map_button_loc[0])
                    time.sleep(1)
                self.logger.info(f"✅ {state.upper()} recolectado desde loop de coins")
                
            elif state == "coin":
                print("--"*10)
                print("CLICKING COIN")
                pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2) 
                time.sleep(2.5) 
                pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2) 
                
                # sometimes clicks already opened coin chests
                background = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
                state = self.determine_state(background)
                if state == "coin":
                    pos = self.locate_x_button(background)
                    pos = pos if pos else self.map_button_loc
                    pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
                    time.sleep(1)  
            else:
                print("--"*10)
                print("NOT COIN")
                pos = self.locate_x_button(background)
                pos = pos if pos else self.map_button_loc
                pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
                time.sleep(1)     

    # ----------------------------------------------------------
    #   SUPPLY COLLECTION
    # ----------------------------------------------------------

    def collect_supply_drop(self, filtered_positions=None):
        """"Collects supply drops
        
        Args:
            filtered_positions: Lista pre-filtrada de posiciones [y, x]. 
                               Si es None, detecta normalmente.
        """

        # use old background to determine stop clicking
        background_old= np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))        
        supply_drop_pos = filtered_positions if filtered_positions is not None else self.detect_supply_drop(background_old)
        
        # Incrementar contador para siguiente detección
        self.supply_counter += 1
        
        # loop until you click supply drop
        for pos in supply_drop_pos:

            if keyboard.is_pressed("q"):
                raise KeyboardInterrupt

            background_old = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
            pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
            time.sleep(0.8)  # AUMENTADO para dar más tiempo a abrir supply drop
            background_new = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))

            # v3.4.8.8.1: RESTAURAR background_changed check para validar que el click abrió ALGO
            # Si después del click la pantalla no cambió = clickeamos en vacío (árbol, pasto, nada)
            # Supply drops SÍ cambian la pantalla (aparece ventana encima del mapa)
            if not self.background_changed(background_old, background_new):
                self.logger.debug(f"⏭️  Click en ({pos[0]}, {pos[1]}) no abrió nada - Saltando objeto")
                continue

            time.sleep(1.2)  # AUMENTADO para dar más tiempo al OCR antes de leer texto
            background_new = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))

            # 🔍 DEBUG: SIEMPRE guardar imágenes de supply drops para analizar OCR
            # Esto nos ayuda a entender POR QUÉ el OCR falla en supplies
            self.debug_save_ocr_regions(background_new, f"supply_{pos[0]}_{pos[1]}")

            state = self.determine_state(background_new)
            
            # 🛡️ v3.4.8.8.0: VALIDACIÓN MEJORADA para force-supply
            # Solo forzar como supply si:
            # 1. Viene de filtered_positions (detección por color)
            # 2. OCR no detectó supply/event/out_of_range/dino
            # 3. El texto OCR es razonable (vacío o contiene letras, NO símbolos raros)
            def is_garbage_ocr(text):
                """Detecta si OCR leyó basura (símbolos extraños, números puros, caracteres especiales)"""
                if not text or text == "":
                    return False  # Texto vacío es aceptable (OCR pudo fallar)
                
                # Contar caracteres extraños
                special_chars = sum(1 for c in text if c in '~»)(%=+-°<>[]{}|\\/@#$^&*_')
                letters = sum(1 for c in text if c.isalpha())
                
                # Si >50% son símbolos especiales, es basura
                if len(text) > 0 and special_chars / len(text) > 0.5:
                    return True
                
                # Si tiene símbolos Y pocas letras, es basura
                if special_chars > 2 and letters < 3:
                    return True
                
                return False
            
            # v3.4.8.7.4: Si viene de filtered_positions y OCR falla, FORZAR como supply
            # v3.4.8.7.7: No forzar dinos como supply (respetar detección correcta de OCR)
            # v3.4.8.8.0: NO forzar si OCR leyó basura/símbolos
            self.logger.debug(f"🔍 Evaluando force-supply: filtered_positions={filtered_positions is not None}, state='{state}'")
            
            if filtered_positions is not None and state not in ["supply", "event", "out_of_range", "dino"]:
                if is_garbage_ocr(state):
                    self.logger.warning(f"❌ OCR leyó BASURA: '{state}' - NO FORZANDO como supply (saltando objeto)")
                    self.logger.debug(f"🔍 Texto OCR considerado basura: '{state}'")
                    continue  # Saltar este objeto, claramente es falso positivo
                else:
                    self.logger.warning(f"⚠️  OCR detectó '{state}' pero viene de filtered_positions - FORZANDO como SUPPLY")
                    state = "supply"
            
            # 🐛 DEBUG: Verificar valor de state antes del if
            self.logger.debug(f"🔍 Valor de state antes del if: '{state}' (type: {type(state)})")
            self.logger.debug(f"🔍 Evaluando: state == 'supply' → {state == 'supply'}")
            self.logger.debug(f"🔍 Evaluando: state == 'event' → {state == 'event'}")
            
            # MEJORADO: También aceptar "event" como supply drop válido
            if state == "supply" or state == "event":
                self.logger.info(f"🎁 Recolectando {state.upper()}...")

                # Tomar screenshot antes del primer click
                background_before_clicks = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
                
                # Click en el centro para girar/abrir el supply drop
                pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2)
                time.sleep(2.5)
                
                # Click adicionales para asegurar recolección
                count = 0
                max_collection_clicks = 3  # Máximo 3 clicks para recolectar
                
                while count < max_collection_clicks:
                    pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2)
                    time.sleep(1.5)
                    count += 1
                    self.logger.debug(f"   Click recolección {count}/{max_collection_clicks}")
                
                # Verificar si regresamos al mapa (supply se cerró automáticamente)
                background_after = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
                
                # Si no se cerró automáticamente, buscar botón X o mapa
                if self.background_changed(background_before_clicks, background_after):
                    self.logger.debug("   Supply aún abierto, buscando botón para cerrar...")
                    pos_x = self.locate_x_button(background_after)
                    if pos_x:
                        pyautogui.click(x=self.x+pos_x[1], y=self.y+pos_x[0])
                        time.sleep(1)
                    else:
                        # Si no hay X, clickear botón de mapa
                        pyautogui.click(x=self.x+self.map_button_loc[1], y=self.y+self.map_button_loc[0])
                        time.sleep(1)
                
                self.logger.info(f"✅ {state.upper()} procesado")

            else:
                # 🔧 v3.4.8.7.2: Si OCR no identifica el objeto, salir
                # Esto maneja casos de RAIDS, JEFES, dinos VIP, etc.
                print("--"*10)
                print(f"NOT SUPPLY DROP (detected: {state})")
                self.logger.warning(f"⚠️  Objeto no identificado como supply drop - Saliendo...")
                pos_x = self.locate_x_button(background_new)
                pos_x = pos_x if pos_x else self.map_button_loc
                pyautogui.click(x=self.x+pos_x[1], y=self.y+pos_x[0])
                time.sleep(1)
                                       

    # ----------------------------------------------------------
    #   HELPER
    # ----------------------------------------------------------

    def background_changed(self, b1, b2, threshold=1500):
        """Compare difference between two frames - REDUCIDO DE 2000 A 1500"""
        diff = (b1.astype(float) - b2.astype(float))**2
        mean_diff = np.mean(diff)
        print(f"[DIFF] {mean_diff:.1f} (threshold: {threshold})")
        return mean_diff > threshold
    
    def check_time_limit(self):
        """
        Verifica si se ha alcanzado el tiempo límite de ejecución
        Retorna True si se debe detener el bot
        """
        if not self.max_run_hours:
            return False
        
        elapsed_hours = (time.time() - self.start_time) / 3600
        
        if elapsed_hours >= self.max_run_hours:
            self.logger.info("="*80)
            self.logger.info("⏰ TIEMPO LÍMITE ALCANZADO")
            self.logger.info("="*80)
            self.logger.info(f"⏱️  Tiempo ejecutado: {elapsed_hours:.2f} horas")
            self.logger.info(f"⏱️  Límite configurado: {self.max_run_hours} horas")
            self.logger.info("🛑 Deteniendo bot para prevenir baneo...")
            return True
        
        # Mostrar progreso cada hora
        if int(elapsed_hours) > 0 and int(elapsed_hours * 60) % 60 == 0:
            remaining = self.max_run_hours - elapsed_hours
            self.logger.info(f"⏱️  Tiempo restante: {remaining:.1f} horas")
        
        return False
    
    def debug_save_ocr_regions(self, background, filename_prefix="debug"):
        """
        FUNCIÓN DE DEBUG: Guarda las regiones de OCR como imágenes
        Útil para verificar qué está leyendo el bot
        
        Uso: Llama a esta función cuando quieras ver qué captura el OCR
        Las imágenes se guardan en la carpeta actual
        """
        try:
            import os
            from PIL import Image
            
            # Crear carpeta de debug si no existe
            debug_folder = "debug_screenshots"
            if not os.path.exists(debug_folder):
                os.makedirs(debug_folder)
            
            # Guardar región del botón de lanzar
            launch_button = background[self.launch_button_loc[0]:self.launch_button_loc[1], 
                                    self.launch_button_loc[2]:self.launch_button_loc[3]]
            Image.fromarray(launch_button).save(f"{debug_folder}/{filename_prefix}_launch_button.png")
            
            # Guardar región del texto de supply drop
            supply_text = background[self.supply_drop_text_loc[0]:self.supply_drop_text_loc[1],
                                    self.supply_drop_text_loc[2]:self.supply_drop_text_loc[3]]
            Image.fromarray(supply_text).save(f"{debug_folder}/{filename_prefix}_supply_text.png")
            
            # Guardar pantalla completa para referencia
            Image.fromarray(background).save(f"{debug_folder}/{filename_prefix}_full_screen.png")
            
            print(f"[DEBUG] Imágenes guardadas en carpeta '{debug_folder}/'")
            
        except Exception as e:
            print(f"[DEBUG] Error al guardar imágenes: {e}")