import pyautogui
import keyboard
import time
import logging

from jw_bot import Bot

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
    
    DEBUG = True

    # for changing location
    something_there = False
    number_of_scrolls = 0
    max_scrolls = 10

    x, y, w, h = -1, -1, -1, -1
    bot = Bot()
    
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

                # get coins
                logger.debug("🪙 Verificando monedas...")
                bot.collect_coin()

                # get supply drops
                logger.debug("📦 Verificando supply drops...")
                bot.collect_supply_drop()                                 

                # get dinos
                logger.debug("🦖 Verificando dinosaurios...")
                bot.collect_dino()

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
        logger.info("⛔ BOT DETENIDO POR USUARIO")
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
