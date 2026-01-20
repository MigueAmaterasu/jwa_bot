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
        self.v_max = 20  # ⚡ v3.4.6: DUPLICADO de 10 a 20 para seguir dinos rápidos
        

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
        # 🎨 COLORES ACTIVOS (normal):
        
        # 🟢 EVENTOS ESPECIALES - Verde brillante
        self.special_event_color = (0, 120, 0, 180, 255, 180)
        # Rango: R[0-180], G[120-255], B[0-180]
        
        # 🟠 SUPPLY DROPS - Naranja/Amarillo
        self.supply_drop_color = (160, 60, 0, 255, 255, 120)
        # Rango: R[160-255], G[60-255], B[0-120]
        
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

        # ⚡ OPTIMIZADO v3.4.4: Tamaño mínimo basado en análisis real de map_initial
        # Análisis: Supply drops reales van de 11-2712 píxeles
        # Con min=50 se perdían 9/19 naranjas (47%) y 1/3 verdes (33%)
        # Nuevo umbral: 15 píxeles = captura todos sin generar falsos positivos
        min_pixels = 15
        
        # v3.4.7: Zonas de exclusión para círculos de evento fijos
        # Coordenadas aproximadas en 565x952 (ajustar según necesidad)
        # Esquina inferior izquierda: X[0-180] Y[600-952] (Especial + Extra/Radar)
        # Esquina inferior derecha: X[385-565] Y[600-952] (Nuevo + Mochila)
        excluded_zones = [
            {'name': 'Inferior izquierda (Especial/Extra)', 'x_min': 0, 'x_max': 180, 'y_min': 600, 'y_max': 952},
            {'name': 'Inferior derecha (Nuevo/Mochila)', 'x_min': 385, 'x_max': 565, 'y_min': 600, 'y_max': 952}
        ]
        
        for label in range(1, labels.max()+1):
            rows, cols = np.where(labels == label)
            if len(rows) > min_pixels:
                center_y = self.shooting_zone[0] + int(np.mean(rows))
                center_x = self.shooting_zone[2] + int(np.mean(cols))
                
                # Verificar si está en zona excluida
                is_excluded = False
                for zone in excluded_zones:
                    if (zone['x_min'] <= center_x <= zone['x_max'] and 
                        zone['y_min'] <= center_y <= zone['y_max']):
                        self.logger.debug(f"   ⛔ Supply drop #{label} en zona excluida: {zone['name']} ({center_y}, {center_x})")
                        is_excluded = True
                        break
                
                if not is_excluded:
                    pos.append([center_y, center_x])
                    self.logger.debug(f"   ✅ Supply drop #{label}: {len(rows)} píxeles en posición ({center_y}, {center_x})")
        
        if len(pos) > 0:
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

        if len(pos) > 0:
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

        # find center of mass
        for label in range(1, labels.max()+1):
            label_dist = dist * (labels == label).astype(np.uint8)
            row, col = np.unravel_index(label_dist.argmax(), label_dist.shape)
            pos.append([self.shooting_zone[0] + row, 
                        self.shooting_zone[2] + col])

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
            

    def determine_state(self, background):
        """After you click determine is this supply drop/dino/coin chase etc."""

        if keyboard.is_pressed("q"):
            raise KeyboardInterrupt

        state = ""
        
        # 🛡️ v3.4.7: FALLBACK DE SEGURIDAD - Buscar X para salir de pantallas problemáticas
        # Si entramos a un círculo de evento por error, detectar la X y clickearla
        pos_x = self.locate_x_button(background)
        if pos_x:
            self.logger.warning("⚠️  [FALLBACK] Detectada X de salida - Clickeando para salir de pantalla problemática")
            pyautogui.click(x=self.x+pos_x[1], y=self.y+pos_x[0])
            time.sleep(1)
            state = "out_of_range"
            return state
        
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
        
        # 4. 🚫 INCUBADORAS - Eventos de combate/asalto
        if any(word in combined_text for word in ["COMBATE", "BATTLE", "ASALTO", "INCUBADORA", "INCUBATOR"]):
            state = "out_of_range"
            self.logger.warning("⛔ [EXCLUIDO] Incubadora o evento de combate detectado")
            return state
        
        # 5. 🏛️ RAIDS - Detectan "JEFE" en el texto
        if "JEFE" in combined_text or "BOSS" in combined_text:
            state = "out_of_range"
            self.logger.warning("⛔ [EXCLUIDO] Raid con jefe detectado")
            return state
        
        # 6. 🛕 SANTUARIOS - Botón dice "ENTRAR"
        if "ENTRAR" in text1 or "ENTER" in text1:
            state = "out_of_range"
            self.logger.warning("⛔ [EXCLUIDO] Santuario detectado (botón ENTRAR)")
            return state
        
        # 7. ⏱️ SUPPLY DROPS EN COOLDOWN - Ya fueron recolectados recientemente
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
        # Prioridad: DINO > SUPPLY > COIN
        
        # 1. Detectar DINOSAURIOS (más específico primero)
        if any(word in combined_text for word in ["LANZAR", "DISPARAR", "LAUNCH", "SHOOT", "CAPTURAR", "CAPTURA"]):
            state = "dino"
            self.logger.debug("   🦖 Palabras clave de DINO detectadas")
        
        # 2. Detectar SUPPLY DROPS (palabras clave específicas)
        # INCLUYE "EVENTO" para farolitos verdes que dicen "EVENTO ESPECIAL TERMINA EN..."
        elif any(word in combined_text for word in ["SUMINISTRO", "SUMINISTROS", "SUPPLY", "DROP", "ABASTECIMIENTO", "EVENTO", "EVENT", "ESPECIAL", "SPECIAL"]):
            state = "supply"
            self.logger.debug("   📦 Palabras clave de SUPPLY detectadas")
            
        # 3. Detectar MONEDAS / COIN CHASE
        elif any(word in combined_text for word in ["MONEDA", "MONEDAS", "COIN", "CHASE", "ORO", "GOLD", "PERSECUCION", "PERSECUCIÓN"]):
            state = "coin"
            self.logger.debug("   🪙 Palabras clave de COIN detectadas")
        
        # 4. Detección por fragmentos parciales (fallback) - EVENTOS YA EXCLUIDOS ARRIBA
        elif any(fragment in combined_text for fragment in ["SUMIN", "DINO", "MONED"]):
            if "SUMIN" in combined_text:
                state = "supply"
                self.logger.debug("   📦 Fragmento 'SUMIN' detectado")
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
        shots_attempted = 0  # Contador de intentos de disparo
        last_shot_attempt = start

        # ⚡ OPTIMIZADO: Reducido timeout de 60 a 45 segundos (suficiente para centrar)
        while not self.is_dino_loading_screen(background) and end - start < 45:
            
            if keyboard.is_pressed("q"):
                raise KeyboardInterrupt

            # b_prev = background
            background = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
            background_cropped = background[self.dino_shoot_loc[0]:,:self.dino_shoot_loc[1],:]
            dino_loc, _ = dino_location(background_cropped, self.dino_shoot_loc[0], 2*self.D)
            
            end = time.time()
            
            # ⚡ NUEVO v3.4.6: Forzar disparo cada 10 segundos si no se ha disparado
            if end - last_shot_attempt > 10 and shots_attempted < 3:
                self.logger.warning(f"⚠️  Forzando disparo #{shots_attempted + 1} (timeout 10s)")
                pyautogui.mouseUp()
                time.sleep(0.3)
                pyautogui.mouseDown()
                time.sleep(0.5)
                shots_attempted += 1
                last_shot_attempt = end

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
                    time.sleep(0.25)
                    pyautogui.mouseDown()
                    time.sleep(0.5)
                else: # if not move screen to dino
                    v_max_new = v_max + h2*battery_left

                    # ⚡ v3.4.6: Factor de predicción AUMENTADO para dinos rápidos
                    # Aumentado de 3x a 5x para anticipar mejor el movimiento
                    prediction_factor = 5.0
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
        
        # ⚡ v3.4.6: Si salió del loop sin disparar, fuerza un disparo final
        if not self.is_dino_loading_screen(background):
            self.logger.warning("⚠️  Salió del loop sin detectar pantalla de carga - Forzando disparo final")
            pyautogui.mouseUp()
            time.sleep(0.5)
        
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

    def collect_dino(self):
        """"Finds and shoots the dino"""
        
        background = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
        dino_pos = self.detect_dino(background)
        
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

            if state == "dino":
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

    def collect_coin(self):
        """Collects coin chests"""
        background = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
        coin_pos = self.detect_coins(background)

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
            if state == "coin":
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

    def collect_supply_drop(self):
        """"Collects supply drops"""

        # use old background to determine stop clicking
        background_old= np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))        
        supply_drop_pos = self.detect_supply_drop(background_old)
        
        # loop until you click supply drop
        for pos in supply_drop_pos:

            if keyboard.is_pressed("q"):
                raise KeyboardInterrupt

            background_old = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
            pyautogui.click(x=self.x+pos[1], y=self.y+pos[0])
            time.sleep(0.3)  # AUMENTADO de 0.2 a 0.3
            background_new = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))

            # to many FPs so quick way to eliminate them
            if not self.background_changed(background_old, background_new):
                print("--"*10)
                print("NOTHING THERE")
                continue

            time.sleep(1.0)  # AUMENTADO de 0.8 a 1.0 para dar más tiempo al OCR
            background_new = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))

            state = self.determine_state(background_new)
            
            # 🔍 DEBUG: Descomentar la siguiente línea para guardar imágenes de lo que ve el OCR
            self.debug_save_ocr_regions(background_new, f"supply_{pos[0]}_{pos[1]}")
            
            # MEJORADO: También aceptar "event" como supply drop válido
            if state == "supply" or state == "event":
                print("--"*10)
                print(f"CLICKING {state.upper()}")

                background_tmp = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
                # activate the supply drop
                pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2)
                time.sleep(2.5)  # AUMENTADO de 2 a 2.5
                background_new = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
                
                # Si no cambió el background, puede que ya esté abierto o necesite cerrar
                if not self.background_changed(background_new, background_tmp):
                    pos_x = self.locate_x_button(background_new)
                    if pos_x:
                        pyautogui.click(x=self.x+pos_x[1], y=self.y+pos_x[0])
                        time.sleep(1) 

                count = 0
                # loop until max click is reached or we are in the old background
                while self.max_click >= count and \
                      self.background_changed(background_old, background_new):
                    print("--"*10)
                    print(f"CLICK {count+1}/{self.max_click}")
                    pyautogui.click(x=self.x+self.w//2, y=self.y+self.h//2)
                    time.sleep(2.5) 
                    background_new = np.array(pyautogui.screenshot(region=(self.x, self.y, self.w, self.h)))
                    count += 1

                # if clicked more than max amount something is wrong
                if count > self.max_click:
                    pos_x = self.locate_x_button(background_new)
                    if pos_x:
                        pyautogui.click(x=self.x+pos_x[1], y=self.y+pos_x[0])
                        time.sleep(1) 

            else:
                print("--"*10)
                print(f"NOT SUPPLY DROP (detected: {state})")
                # find x button if not there click on map button
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