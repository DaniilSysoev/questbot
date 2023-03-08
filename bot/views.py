from django.shortcuts import HttpResponse
import telebot as tb
from django.conf import settings


bot = tb.TeleBot(settings.BOT_TOKEN)

def index(request):
    # bot.set_webhook('https://9e93-83-242-179-137.eu.ngrok.io/')
    if request.method == "POST":
        update = tb.types.Update.de_json(request.body.decode('utf-8'))
        bot.process_new_updates([update])

    return HttpResponse('<h1>Ты подключился!</h1>')