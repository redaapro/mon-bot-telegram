import telegram
from binance.client import Client
from binance.enums import *
import ccxt

# Créer une instance de l'échange Binance pour le testnet
exchange = ccxt.binance({
    'apiKey': 'R4QSUtViCHu7VgT38qSWQyc6v6owv3zVKCQUFHTu6UIdzTgNQcEWYnsrAehm93k0',
    'secret': 'CslfmKZDzIOn6PhoGgWkGLb1QVre6mVSxPuMG6WnemyqALVjAf473rAP3uN9cUan',
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future', # utiliser 'spot' pour le trading spot
        'test': True # activer l'environnement de test
    }
})

# Vérifier la connexion
print(exchange.fetch_ticker('BTC/USD'))

# configure Telegram bot
bot_token = '5973275160:AAGdcqAdOQDCEOxcUo5Kbuzmc8FPEZrkfpA'
bot_chatID = '1531272752'
bot = telegram.Bot(token=bot_token)

# set symbol and quantity
symbol = 'BTC/USD'
quantity = 0.02

# set order type and side
order_type = ORDER_TYPE_MARKET
order_side = None

# listen for messages on Telegram
last_update_id = None
while True:
    # get new messages
    updates = bot.get_updates(offset=last_update_id)
    if updates:
        last_update_id = updates[-1].update_id + 1
        for update in updates:
            message = update.message.text
            chat_id = update.message.chat_id
            
            # check if message is a trade signal
            if message.startswith('ACHAT') or message.startswith('VENTE'):
                # set order side
                if message.startswith('ACHAT'):
                    order_side = SIDE_BUY
                elif message.startswith('VENTE'):
                    order_side = SIDE_SELL
                else:
                    continue
                
                # place order on Binance
                try:
                    order = exchange.create_order(
                        symbol=symbol,
                        side=order_side,
                        type=order_type,
                        quantity=quantity
                    )
                except Exception as e:
                    bot.send_message(chat_id=chat_id, text=f"Une erreur s'est produite lors de la passation de l'ordre: {e}")
                    continue
                
                # send confirmation message privately
                bot.send_message(chat_id=bot_chatID, text=f"Un nouvel ordre a été placé:\n\nSymbole: {symbol}\nCôté: {order_side}\nType: {order_type}\nQuantité: {quantity}")
            
            # check if message is a trade exit signal
            elif message.startswith('PRENEZ LE TP1 MAINTENANT'):
                # close position on Binance
                try:
                    position = exchange.futures_position_information(symbol=symbol)
                    if position[0]['positionAmt'] == '0':
                        bot.send_message(chat_id=chat_id, text="Il n'y a pas de position à fermer")
                        continue
                    
                    order = exchange.create_order(
                        symbol=symbol,
                        side=SIDE_SELL if position[0]['positionSide'] == 'LONG' else SIDE_BUY,
                        type=ORDER_TYPE_MARKET,
                        quantity=abs(float(position[0]['positionAmt']))
                    )
                except Exception as e:
                    bot.send_message(chat_id=chat_id, text=f"Une erreur s'est produite lors de la fermeture de la position: {e}")
                    continue
                
                # send confirmation message privately
                bot.send_message(chat_id=bot_chatID, text=f"La position a été fermée:\n\nSymbole: {symbol}\nCôté: {'SELL' if position[0]['positionSide'] == 'LONG' else 'BUY'}\nType: {order_type}\nQuantité: {abs(float(position[0]['positionAmt']))}")
