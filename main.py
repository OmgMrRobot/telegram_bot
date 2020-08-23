import telebot
from collections import defaultdict as def_dict
from telebot import types
import db_script
import time
import pass_key

Token = pass_key.token

add, name, picture, res_location, confirmation = range(5)

user_state = def_dict(lambda: add)

def get_state(message): # узнает состояние
    return user_state[message.chat.id]
def update_state(message, state): # обновляет состояние
    user_state[message.chat.id] = state

restarans = def_dict(lambda: {}) # словарь для ресторанов

def update_restarans(user_id, key, value):
    restarans[user_id][key] = value
def get_resarans(user_id):
    return restarans[user_id]


bot = telebot.TeleBot(Token, parse_mode=None)  # You can set parse_mode by default. HTML or MARKDOWN

@bot.message_handler(commands=['start'])
def handler_message(message):

    markup = types.InlineKeyboardMarkup(row_width=3)
    item1 = types.InlineKeyboardButton("add", callback_data='add')
    item2 = types.InlineKeyboardButton("reset", callback_data='reset')
    item3 = types.InlineKeyboardButton("list", callback_data='list')
    markup.add(item1, item2, item3)

    bot.send_message(message.chat.id,
                     "Добро пожаловать, {0.first_name}!\nЯ - <b>{1.first_name}</b>, бот созданный чтобы быть подопытным кроликом.\n Я могу запоминать название ресторанов, их фотографии и локацию".format(
                         message.from_user, bot.get_me()),
                     parse_mode='html', reply_markup=markup)

def reset_(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    item1 = types.InlineKeyboardButton("add", callback_data='add')
    markup.add(item1)

    db_script.reset(message.chat.id)
    bot.send_message(message.chat.id, text='База чиста', parse_mode='html', reply_markup=markup)


@bot.callback_query_handler(func=lambda message: message.data == 'reset') # срабатывает на кнопку
def handler_message(message):
    reset_(message.message)


@bot.message_handler(commands=['reset']) # срабатывает на команду
def handler_message(message):
    reset_(message)



def lits_(message):
    data = db_script.list(message.chat.id)
    counter = 0
    if data:
        for i in data:
            counter += 1
            bot.send_message(message.chat.id, text=f'---------- location {counter} ------------ ')
            bot.send_photo(message.chat.id, open(i[3], 'rb'), caption=f'Название ресторана: {i[2]}')
            bot.send_location(message.chat.id, i[5], i[4])  # latitude(широта), longitude(долгота)
    else:
        bot.send_message(message.chat.id, text='База пуста')


@bot.callback_query_handler(func=lambda message: message.data == 'list')   # срабатывает на кнопку
def handler_message(message):
    lits_(message.message)

@bot.message_handler(commands=['list']) # срабатывает на команду
def handler_message(message):
    lits_(message)

@bot.callback_query_handler(func=lambda message: message.data == 'add')
def handler_message(message):
    bot.send_message(message.message.chat.id, text='Напиши название ресторана')
    update_state(message.message, name)

@bot.message_handler(commands=['add']) # срабатывает на команду
def handler_message(message):
    bot.send_message(message.chat.id, text='Напиши название ресторана')
    update_state(message, name)


@bot.message_handler(func=lambda message: get_state(message) == name)
def handler_message(message):
    update_restarans(message.chat.id, 'name', message.text)
    bot.send_message(message.chat.id, text='Добавь фотографию ресторана')
    update_state(message, picture)


@bot.message_handler(content_types=['photo'], func=lambda  message: get_state(message) == picture)
def handler_message(message):
    if message.photo:
        try:
            file_info = bot.get_file(message.photo[0].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            filepath = r'C:/Users/GoodMan/Desktop/telegram_bot/media/'

            src = filepath + message.photo[0].file_id
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)
            bot.reply_to(message, "Фото добавлено")
            # print(src)

        except Exception as e:
            bot.reply_to(message, e)

        update_restarans(message.chat.id, 'picture', src)
        bot.send_message(message.chat.id, text='Добавь геопозицию ресторана')
        update_state(message, res_location)
    else:
        bot.send_message(message.chat.id, text=f'Вы прислали не фото: {message.text}.\n Попробуйте еще раз')
        update_state(message, picture)

@bot.message_handler(func=lambda  message: get_state(message) == res_location, content_types= 'location')
def handler_message(message):
    if message.location:

        latitude = message.location.latitude
        longitude = message.location.longitude

        update_restarans(message.chat.id, 'res_location', [longitude, latitude])
        restaran = get_resarans(message.chat.id)
        update_state(message, confirmation)

        markup = types.InlineKeyboardMarkup(row_width=2)
        item1 = types.InlineKeyboardButton("Да", callback_data='Yes')
        item2 = types.InlineKeyboardButton("Нет", callback_data='No')
        markup.add(item1, item2)

        bot.send_message(message.chat.id, \
        text=f'Напиши Да, если все правильно: \nНазвание: {restaran["name"]} \nГеопозиция: {restaran["res_location"]}',
                         parse_mode='html', reply_markup=markup)

    else:
        bot.send_message(message.chat.id, text=f'Вы прислали не локацию: {message.text}.\n Попробуйте еще раз')
        update_state(message, res_location)

@bot.callback_query_handler(func=lambda message: True)
# @bot.message_handler(func=lambda  message: get_state(message) == confirmation )
def handler_message(message):

    restaran = get_resarans(message.message.chat.id)

    markup = types.InlineKeyboardMarkup(row_width=3)
    item1 = types.InlineKeyboardButton("add", callback_data='add')
    item2 = types.InlineKeyboardButton("reset", callback_data='reset')
    item3 = types.InlineKeyboardButton("list", callback_data='list')
    markup.add(item1, item2, item3)

    if message.data == 'Yes':
        bot.send_message(message.message.chat.id, text='Сохранино в базу', parse_mode='html', reply_markup=markup)
        db_script.add_notice(message.message.chat.id, restaran)
        update_state(message.message, add)

    else:
        bot.send_message(message.message.chat.id, text='Попробуем еще раз)', parse_mode='html', reply_markup=markup)
        update_state(message.message, add)




if __name__ == "__main__":
    try:
        bot.polling()
    except:
        time.sleep(20)
        bot.polling()


