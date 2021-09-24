
import telebot
import requests
import urllib.parse
import os

from tinydb import TinyDB
from bs4 import BeautifulSoup


def get_cursos_free(number_page=1) -> None:
    db = TinyDB('db.json')
    db.drop_tables()
    for i in range(number_page):
        response = requests.get(f'https://blog.facialix.com/page/{i}/')
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        body = soup.body
        div_content = body.find('section', {'id': 'content'})
        links_a = div_content.find_all('a', {'class': 'post-comments'})
        links = [a['href'] for a in links_a]

        for link in links:
            response_page = requests.get(link)
            html = response_page.text
            soup = BeautifulSoup(html, 'html.parser')
            body = soup.body
            elements_a = body.find_all('a', {'class': 'wp-block-button__link'})
            for curso in elements_a:
                if 'udemy.com' in curso['href']:
                    cupon = curso['href']
                    link_cupon = cupon.split('=')[-1:]
                    db.insert({'link': urllib.parse.unquote(link_cupon[0])})


def show_db():
    return TinyDB('db.json')
    

TOKEN = os.getenv('TOKEN_BOT')
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, '''
    Comandos que puedes usar
    /start  -   Muestra el mensaje de bienvenida.
    /echo   -   return True si el sistema funciona
    /update -   actualiza los cupones
    /show   -   Muestra los cupones de ese día
     ''')

@bot.message_handler(commands=['echo'])
def send_echo(message):
    bot.reply_to(message, True)


@bot.message_handler(commands=['update'])
def send_echo(message):
    print('[INICIO]')
    get_cursos_free(3)
    print('[FIN]')
    bot.reply_to(message, 'update correctamente')

@bot.message_handler(commands=['show'])
def send_echo(message):
    db = show_db()
    for item in db:
        bot.reply_to(message, item['link'])


@bot.message_handler(func=lambda m: True)
def echo_all(message):
	bot.reply_to(message, message.text)

bot.polling()
