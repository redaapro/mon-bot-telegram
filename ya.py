import os
import telegram
from binance.exceptions import BinanceAPIException
from binance.client import Client
import time
import asyncio
import logging
from flask import Flask

app = Flask(__name__)

port = int(os.environ.get('PORT', 5000))

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info('Starting bot...')

api_key = 'dcsgO7M8Rxizd2ZkmNrCrzPRXFn8c6PHCYSWZgPkGtUaqDOLhTLLR3dsRi9maNUj'
api_secret = 'GXlOr9brewwvoeOV4oJpD01z8Teq9VESABnvDTnF9dJNkzRCyxsIY8pLhJH11kBE'

# Connexion à l'API de Binance
client = Client(api_key, api_secret)

# Création d'une instance de bot Telegram
bot = telegram.Bot(token='5973275160:AAGdcqAdOQDCEOxcUo5Kbuzmc8FPEZrkfpA')
# ID du canal Telegram où les messages seront envoyés
channel_id = '@tradingdongcopy'

# Liste des traders à suivre
traders_to_follow = ["TReeOfAlpha1", "Blockchain_C", "香蕉奶菜"]

@app.route('/')
def index():
    return 'Hello, World!'

@app.route('/bot')
def bot():
    return 'This is the Binance Telegram bot.'

async def main():
    # Envoyer un message de démarrage
    await bot.send_message(chat_id=channel_id, text="Bonjour, bienvenue dans le canal qui tenvoie en temps réels les trades des traders sélectionnés sur Binance. Copier/coller dans votre plateforme de trading !")

    trader_states = {}

    while True:
        try:
            # Récupérer les positions ouvertes pour tous les utilisateurs sur Binance futures
            positions = client.futures_position_information()

            # Récupérer les positions des traders sélectionnés
            selected_positions = [position for position in positions if position['symbol'].startswith(tuple(traders_to_follow))]

            # Trier les positions par rendement
            selected_positions = sorted(selected_positions, key=lambda x: float(x['unRealizedProfit']), reverse=True)

            # Vérifier chaque position du trader dans la liste
            for position in selected_positions:
                trader = position['symbol'][:-4]

                # Récupérer l'historique des transactions pour le trader
                trades = client.futures_account_trades(symbol='')

                # Vérifier si le trader a une position ouverte
                for trade in trades:
                    if trade['buyer'] == trader or trade['seller'] == trader:
                        state = True
                        direction = trade['side']
                        symbol = trade['symbol']
                        entry_price = trade['price']

                        # Vérifier si l'état du trader a changé
                        if state != trader_states[trader]:
                            trader_states[trader] = state

                            # Envoyer un message Telegram avec les informations de la position
                            message = f"🚨 Nouvelle alerte de trading 🚨 {trader} a ouvert une position {direction} de {symbol}, entrée à {entry_price}"
                            await bot.send_message(chat_id=channel_id, text=message)

            # Attendre 30 secondes avant de vérifier à nouveau
            await asyncio.sleep(30)

        except BinanceAPIException as e:
            print(e)
            await asyncio.sleep(30)

if __name__ == '__main__':
    asyncio.run(main())
