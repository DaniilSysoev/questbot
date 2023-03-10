from django.shortcuts import HttpResponse
import telebot as tb
from django.conf import settings
from . import models
import os
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import httplib2


bot = tb.TeleBot(settings.BOT_TOKEN)
# https://api.telegram.org/bot5813570276:AAHVVgjcZZzmYr0Vrb-X9DXq-WHsrsXqLdo/setWebhook?url=https://aa74-95-64-192-254.eu.ngrok.io/bot/

def index(request):
    if request.method == "POST":
        update = tb.types.Update.de_json(request.body.decode('utf-8'))
        bot.process_new_updates([update])
    return HttpResponse('<h1>Ты подключился!</h1>')


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


def create_markup_text(message):
    markup = tb.types.ReplyKeyboardMarkup(resize_keyboard=True)
    last_button = models.UserModel.objects.get(foreign_id=message.from_user.id).last_button_id
    btn = [tb.types.KeyboardButton(i.button) for i in models.ButtonModel.objects.filter(from_button_id=last_button)]
    markup.add(*btn)
    text = models.TextModel.objects.get(button_id=last_button).text
    return text, markup


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
    markup = create_markup_text(message)
    bot.send_message(message.from_user.id, markup[0], reply_markup=markup[1])


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
        command = message.text.split()[:2]
        text = message.text.replace(' '.join(command)+' ', '')
        bot.send_message(command[1], text)
        bot.send_message(message.from_user.id, f'Сообщение отправлено пользователю {command[1]}:\n\n{text}')
    else:
        bot.send_message(message.from_user.id, 'У вас нет доступа к этой команде')


@bot.message_handler(content_types=['text'])
def text(message):
    #if message.text.split()[-1].isdigit():
    #    user = models.UserModel.objects.filter(foreign_id=message.from_user.id)
    #    user.update(stage=int(message.text.split()[-1]))
    #else:
    #    user = models.UserModel.objects.filter(foreign_id=message.from_user.id)
    #    user.update(stage=1)
    if message.text == 'Выход':
        markup = tb.types.InlineKeyboardMarkup()
        button1 = tb.types.InlineKeyboardButton('Продолжить', callback_data='continue')
        button2 = tb.types.InlineKeyboardButton('Начать заново', callback_data='again')
        bot.send_message(message.from_user.id, 'Игра остановлена.', reply_markup=tb.types.ReplyKeyboardRemove())
        markup.add(button1)
        markup.add(button2)
        bot.send_message(message.from_user.id, 'Что вы будете делать?', reply_markup=markup)
    user = models.UserModel.objects.filter(foreign_id=message.from_user.id)
    to_button = models.ButtonModel.objects.get(from_button_id=user[0].last_button_id, button=message.text).to_button_id
    user.update(last_button_id=to_button)
    markup = create_markup_text(message)
    exit_button = tb.types.KeyboardButton('Выход')
    markup[1].add(exit_button)
    bot.send_message(message.from_user.id, markup[0], reply_markup=markup[1])


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == 'continue':
        markup = create_markup_text(call)
        exit_button = tb.types.KeyboardButton('Выход')
        markup[1].add(exit_button)
        bot.send_message(call.from_user.id, markup[0], reply_markup=markup[1])
    elif call.data == 'again':
        user = models.UserModel.objects.filter(foreign_id=call.from_user.id)
        user.update(last_button_id='приветствие')
        markup = create_markup_text(call)
        bot.send_message(call.from_user.id, markup[0], reply_markup=markup[1])