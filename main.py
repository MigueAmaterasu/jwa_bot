import pyautogui
import keyboard
import time
import logging
import platform
import subprocess
import numpy as np

from jw_bot import Bot

# ============================================================================
# ⏱️ CONFIGURACIÓN DE TIEMPO LÍMITE
# ============================================================================
# Establece cuántas horas quieres que corra el bot antes de detenerse
# Esto ayuda a prevenir baneos por jugar demasiado tiempo seguido
# 
# Ejemplos:
#   MAX_RUN_HOURS = 4    # Se detendrá después de 4 horas
#   MAX_RUN_HOURS = 8    # Se detendrá después de 8 horas
#   MAX_RUN_HOURS = 12   # Se detendrá después de 12 horas
#   MAX_RUN_HOURS = None # Correrá indefinidamente (no recomendado)
# ============================================================================
MAX_RUN_HOURS = 10  # ⬅️ CAMBIA ESTE VALOR SEGÚN TUS NECESIDADES

# 💻 APAGADO AUTOMÁTICO DE PC
# Si es True, apagará la PC cuando termine el tiempo límite
# Si es False, solo detendrá el bot

SHUTDOWN_WHEN_DONE = True

if __name__ == "__main__":
    # Obtener logger
    logger = logging.getLogger('JWA_Bot')
    
    logger.info("="*80)
    logger.info("🎮 INSTRUCCIONES DE CALIBRACIÓN")
    logger.info("="*80)
    logger.info("1️⃣  Abre BlueStacks con Jurassic World Alive en el MAPA")
    logger.info("2️⃣  Presiona 'a' y haz click en ESQUINA SUPERIOR IZQUIERDA del juego")
    logger.info("3️⃣  Presiona 'a' otra vez y haz click en ESQUINA INFERIOR DERECHA")
    logger.info("4️⃣  El bot empezará a funcionar automáticamente")
    logger.info("❌ Presiona 'q' para detener el bot en cualquier momento")
    logger.info("="*80)
    
    DEBUG = False

    # for changing location
    something_there = False
    number_of_scrolls = 0
    max_scrolls = 10

    x, y, w, h = -1, -1, -1, -1
    bot = Bot(max_run_hours=MAX_RUN_HOURS)  # Pasamos el tiempo límite al bot
    
    def shutdown_pc():
        """Apaga la PC según el sistema operativo"""
        logger.info("="*80)
        logger.info("💤 INICIANDO APAGADO AUTOMÁTICO DE PC")
        logger.info("="*80)
        
        system = platform.system()
        try:
            if system == "Windows":
                # Windows: shutdown /s /t 60 (apagar en 60 segundos)
                logger.info("🪟 Windows detectado - Apagando en 60 segundos...")
                logger.info("💡 Puedes cancelar con: shutdown /a")
                time.sleep(3)  # 3 segundos para que veas el mensaje
                subprocess.run(["shutdown", "/s", "/t", "60"], check=True)
                logger.info("✅ Comando de apagado enviado correctamente")
            elif system == "Darwin":  # macOS
                logger.warning("🍎 macOS detectado - Apagado automático NO implementado")
                logger.info("💡 Detén el bot manualmente (Ctrl+C)")
            elif system == "Linux":
                logger.warning("🐧 Linux detectado - Apagado automático requiere sudo")
                logger.info("💡 Ejecuta manualmente: sudo shutdown -h +1")
            else:
                logger.warning(f"⚠️  Sistema {system} no soportado para apagado automático")
        except Exception as e:
            logger.error(f"❌ Error al intentar apagar: {e}")
            logger.info("💡 En Windows, ejecuta manualmente: shutdown /s /t 60")
    
    try:
        while True:
            # set location of the app
            if keyboard.is_pressed('a'):
                logger.info("🔘 Tecla 'a' presionada")
                if x == -1 or y == -1:
                    x, y = pyautogui.position()
                    logger.info(f"✅ Primer punto capturado: ({x}, {y})")
                    logger.info("👉 Ahora presiona 'a' de nuevo y haz click en la esquina inferior derecha")
                elif w == -1 or h == -1:
                    x_, y_ = pyautogui.position()
                    logger.info(f"✅ Segundo punto capturado: ({x_}, {y_})")
                    w = abs(x - x_)
                    h = abs(y - y_)
                    bot.set_app_loc(x, y, w, h)
                    logger.info("🚀 Calibración completa! El bot comenzará a operar...")
                    time.sleep(1)

            # take photo
            if bot.loc:
                
                if keyboard.is_pressed("q"):
                    raise KeyboardInterrupt
                
                # Verificar tiempo límite
                if bot.check_time_limit():
                    raise KeyboardInterrupt

                # 🔄 v3.4.8.9.8: NUEVA LÓGICA - Revisar mismas posiciones hasta limpiar el mapa
                # Detectar TODOS los objetos una sola vez
                logger.debug("🔍 Escaneando mapa...")
                screenshot = np.array(pyautogui.screenshot(region=(bot.x, bot.y, bot.w, bot.h)))
                
                coins = bot.detect_coins(screenshot)
                supply_drops = bot.detect_supply_drop(screenshot)
                dinos = bot.detect_dino(screenshot)
                
                # Filtrar por zonas prohibidas
                valid_coins = bot.filter_excluded_zones(coins, "coin")
                valid_drops = bot.filter_excluded_zones(supply_drops, "supply")
                valid_dinos = bot.filter_excluded_zones(dinos, "dino")
                
                # Contar objetos totales
                total_objects = len(valid_coins) + len(valid_drops) + len(valid_dinos)
                
                if total_objects > 0:
                    logger.info(f"📊 Objetos detectados: {len(valid_coins)}🪙 {len(valid_drops)}📦 {len(valid_dinos)}🦖 (Total: {total_objects})")
                    
                    # Recolectar en orden: coins → supplies → dinos
                    # NOTA: Cada collect_*() internamente verifica con determine_state() 
                    # si el objeto ya fue recolectado, está en cooldown, o no existe
                    if valid_coins:
                        logger.info(f"🪙 Recolectando {len(valid_coins)} monedas...")
                        bot.collect_coin(filtered_positions=valid_coins)
                    
                    if valid_drops:
                        logger.info(f"📦 Recolectando {len(valid_drops)} supply drops...")
                        bot.collect_supply_drop(filtered_positions=valid_drops)
                    
                    if valid_dinos:
                        logger.info(f"🦖 Disparando a {len(valid_dinos)} dinosaurios...")
                        bot.collect_dino(filtered_positions=valid_dinos)
                    
                    # ⚠️ NO CAMBIAR DE VISTA - volver a escanear misma zona
                    # El siguiente escaneo solo detectará objetos que NO fueron recolectados
                    # (los que tienen cooldown, están fuera de rango, o son nuevos spawns)
                    logger.info("🔄 Revisando misma zona de nuevo para detectar objetos restantes...")
                    continue  # Volver al inicio del loop sin cambiar vista
                    
                else:
                    # ✅ Zona limpia - cambiar de vista
                    if coins or supply_drops or dinos:
                        logger.info(f"⚠️  Objetos en zonas prohibidas: {len(coins)-len(valid_coins)}🪙 {len(supply_drops)-len(valid_drops)}📦 {len(dinos)-len(valid_dinos)}🦖")
                    logger.info("✅ Zona limpia - cambiando vista del mapa...")


                if bot.number_of_scrolls > max_scrolls:
                    # move location
                    logger.info("="*80)
                    logger.info("📍 CAMBIANDO UBICACIÓN EN EL MAPA")
                    logger.info("="*80)
                    bot.change_location()
                    bot.number_of_scrolls = 0
                    
                # if not something_there:
                bot.change_view()
                bot.number_of_scrolls += 1
                

            time.sleep(0.1)
            
    except KeyboardInterrupt:
        logger.info("="*80)
        logger.info("⛔ BOT DETENIDO POR USUARIO (Ctrl+C o 'q')")
        logger.info("="*80)
        logger.info("📊 RESUMEN DE RECURSOS COLECTADOS:")
        logger.info("-"*80)
        
        if bot.supply_collected:
            logger.info("📦 SUMINISTROS:")
            for key, value in bot.supply_collected.items():
                logger.info(f"   • {key}: {value}")
        else:
            logger.info("📦 SUMINISTROS: Ninguno")
            
        if bot.dino_collected:
            logger.info("🦖 DINOSAURIOS:")
            for key, value in bot.dino_collected.items():
                logger.info(f"   • {key}: {value}")
        else:
            logger.info("🦖 DINOSAURIOS: Ninguno")
            
        logger.info("="*80)
        logger.info("✅ Sesión finalizada. Log guardado en carpeta 'logs/'")
        logger.info("="*80)
        
        # Verificar si se debe apagar la PC
        if SHUTDOWN_WHEN_DONE and bot.max_run_hours and (time.time() - bot.start_time) / 3600 >= bot.max_run_hours:
            logger.info("⏰ Tiempo límite alcanzado - Apagando PC...")
            shutdown_pc()
