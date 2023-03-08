from django.shortcuts import HttpResponse
import telebot as tb
from django.conf import settings
from . import models
import os
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import httplib2


bot = tb.TeleBot(settings.BOT_TOKEN)
# https://api.telegram.org/bot5813570276:AAHVVgjcZZzmYr0Vrb-X9DXq-WHsrsXqLdo/setWebhook?url=https://0de0-83-242-179-142.eu.ngrok.io/bot/

def get_service_sacc():
    creds_json = os.path.dirname(__file__) + '/movement-quest-bot-c444b617c5db.json'
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds_service = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scopes).authorize(httplib2.Http())
    return build('sheets', 'v4', http=creds_service)


def read_plot(sheet_name):
    service = get_service_sacc()
    sheet = service.spreadsheets()
    sheet_id = models.PlotModel.objects.all().order_by('-id')[0].link
    resp = sheet.values().get(spreadsheetId=sheet_id, range=sheet_name).execute()
    return resp


def index(request):
    if request.method == "POST":
        update = tb.types.Update.de_json(request.body.decode('utf-8'))
        bot.process_new_updates([update])
    return HttpResponse('<h1>Ты подключился!</h1>')


@bot.message_handler(commands=['start'])
def start(message: tb.types.Message):
    p, _ = models.UserModel.objects.get_or_create(
        foreign_id=message.from_user.id,
        defaults={
            'root': False,
            "stage": 0,
            'last_button_id': 'приветствие'
        }
    )
    bot.send_message(message.from_user.id, f'Приветствуем тебя, {message.from_user.full_name}!')


@bot.message_handler(commands=['auth'])
def auth(message: tb.types.Message):
    text = list(message.text.split())
    if len(text) == 2:
        if text[1] == settings.AUTH_ADMIN_TOKEN:
            models.UserModel.objects.filter(foreign_id=message.from_user.id).update(root=True)
            bot.send_message(message.from_user.id, 'Root права получены')


@bot.message_handler(commands=['plot'])
def plot(message: tb.types.Message):
    if models.UserModel.objects.get(foreign_id=message.from_user.id).root == True:
        text = list(message.text.split())
        if len(text) == 1:
            bot.send_message(message.from_user.id, models.PlotModel.objects.all().order_by('-id')[0].link)
        elif len(text) == 2:
            models.PlotModel(link=text[1]).save()
            bot.send_message(message.from_user.id, 'Новая ссылка загружена')
    else:
        bot.send_message(message.from_user.id, 'У вас нет доступа к этой команде')


@bot.message_handler(commands=['update'])
def plot(message: tb.types.Message):
    if models.UserModel.objects.get(foreign_id=message.from_user.id).root == True:
        bot.send_message(message.from_user.id, 'Удаляю старый сюжет...')
        models.TextModel.objects.all().delete()
        bot.send_message(message.from_user.id, 'Сюжет удален')
        bot.send_message(message.from_user.id, 'Считываю новый сюжет...')
        plot = read_plot('script')['values'][:0:-1]
        for i in plot:
            models.TextModel(button_id=i[0], text=i[1]).save()
        bot.send_message(message.from_user.id, 'Новый сюжет добавлен')
        bot.send_message(message.from_user.id, 'Удаляю старые кнопки...')
        models.ButtonModel.objects.all().delete()
        bot.send_message(message.from_user.id, 'Кнопки удалены')
        bot.send_message(message.from_user.id, 'Считываю новые кнопки...')
        buttons = read_plot('button')['values'][:0:-1]
        for i in buttons:
            models.ButtonModel(from_button_id=i[0], button=i[1], to_button_id=i[2]).save()
        bot.send_message(message.from_user.id, 'Новые кнопки добавлены')
    else:
        bot.send_message(message.from_user.id, 'У вас нет доступа к этой команде')


@bot.message_handler(commands=['message'])
def message(message: tb.types.Message):
    if models.UserModel.objects.get(foreign_id=message.from_user.id).root == True:
        bot.send_message(message.text.split()[1], message.text.split()[2])
        bot.send_message(message.from_user.id, f'Сообщение отправлено {message.text.split()[1]}({message.text.split()[1].full_name}):\n\n{message.text.split()[2]}')