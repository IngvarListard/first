# -*- coding: utf-8 -*-
import os
import config
import telebot
import json
from natsort import natsorted
from flask import Flask, request


server = Flask(__name__)
token = '486658164:AAEKCXMICg9R1njGG_hCSLAsGyNl0rC_p-c'
bot = telebot.TeleBot(token, threaded=False) # Обращение к боту + токен
types = telebot.types # Types for markup
ee_db = json.load(open(config.eedb_file)) # Открытие БД
pe_db = json.load(open(config.pedb_file))
markup_list1 = ['Level 1', 'Level 2', 'Level 3', 'Level 4']
command = [['eel1ep' + str(x) for x in range(1, 9)],
           ['eel2ep' + str(x) for x in range(1, 9)],
           ['eel3ep' + str(x) for x in range(1, 21)],
           ['eel4hi', 'eel4bh1', 'eel4bh2', 'eel4bh3', 'mst', 'wg', 'ab']]
command_list = []
for i in command: command_list.extend(i) # объединение списков команд
command = [['pe0' + str(x) for x in range(1, 10)],['pe' + str(x) for x in range(10, 31)]]
pe_command_list = []
for i in command: pe_command_list.extend(i) # объединение списков команд
command_list.extend(pe_command_list)


@server.route('/' + token, methods=['POST'])
def getMessage():
    print('GOT IT!')
    bot.process_new_messages([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://safe-refuge-18942.herokuapp.com/' + token)
    return "!", 200


def smes(message, text): # Облегчаем жизнь отправки сообщений
    bot.send_message(message.chat.id, text)

# Должно приходить количество строк, возможно информация для строк, будут выводиться кнопки
def markup_generator(markup_list):

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup_items = []
    # Костыли костылики для преобразования списка в строку
    # и удаление "ненужных" символов для красивого вывода
    symbols = ['[',']', '"', "'"]
    listr = str(markup_list)

    for symbol in symbols:
        if symbol in listr:
            listr = listr.replace(symbol, '')

    for item in listr.split(','):
        markup_items.append(item)

    for item in markup_items:
        markup.add(item)

    return markup


# Зохват /start, /help
@bot.message_handler(commands=['start','help'])
def help_request(message):

    smes(message, 'Добро пожаловать на аудиокурсы Английского языка by A.J. Hoge.'
                  '\nВведите /learn чтобы приступить к обучению')

# Зохват для вывода списка курсов. Вероятно стоит добавить проверку "игры" из статьи
@bot.message_handler(commands=['learn'])
def learn(message):

    smes(message, 'Пожалуйста выберите курс, который хотите изучить'
                  '\n1.Effortless English\n2.Power English')

    markup_list = ['1.Effortless English', '2.Power English']

    bot.send_message(message.chat.id, "Выберите курс:",
                     reply_markup=markup_generator(markup_list))


# Генератор ответов на запросы со слэшем. Желательно
# записать в "базу" чтобы не генерировать каждый раз.
@bot.message_handler(commands=command_list)
def response_generator(message):

    if message.text[:3] == '/ee':
        # Получение уровня из сообщения постыдным способом
        dic_number = message.text.split('eel')[1].split('ep')[0]
        # Получение темы из сообщения постыдным способом
        theme_number = message.text.split('eel')[1].split('ep')[1]
        # Получение списка уровней из ключей базы
        ee_keylist = natsorted(list(ee_db['Effortless English']))[0:4]
        # Получение ключа уровня для вызова из словаря
        ee_levelkey = ee_keylist[int(dic_number) - 1]
        # Получение списка из значения словаря нужного уровня
        ee_themekey = natsorted(list(ee_db['Effortless English'][ee_levelkey]))
        # Целевой словарь с ид файлов
        target_dic = ee_db['Effortless English'][ee_levelkey][ee_themekey[int(theme_number) - 1]]

        for file in target_dic.values():
            bot.send_document(message.chat.id, file)

    elif message.text[:3] == '/pe':

        # Схожая с предыдущим схема, базы делал в разное время и
        # разными подходами, логика немного различна
        pe_story_number = int(message.text[-2:])
        pe_keylist = natsorted(list(pe_db))
        pe_storykey = pe_keylist[pe_story_number - 1]

        for file in pe_db[pe_storykey]['audio'].values():
            bot.send_audio(message.chat.id, file)

        for file in pe_db[pe_storykey]['documents'].values():
            bot.send_document(message.chat.id, file)

    elif message.text == '/mst':
        place_key = ee_db['Effortless English']['mini_story_transcripts.pdf']
        bot.send_document(message.chat.id, place_key)

    elif message.text == '/wg':
        place_key = ee_db['Effortless English']['welcome_guide.pdf']
        bot.send_document(message.chat.id, place_key)

    elif message.text == '/ab':
        place_key = pe_db['Commentary Audio Bonuses']

        for file in place_key['audio'].values():
            bot.send_audio(message.chat.id, file)

        for file in place_key['documents'].values():
            bot.send_document(message.chat.id, file)

# commands_dic = {message.text: ee_themekey[int(theme_number) - 1]} Желательно создать базу с реквестами

# Ловим ответ
@bot.message_handler(func=lambda message: True, content_types=['text'])
def choose_course(message):

    if message.text == '2.Power English':

        smes(message, 'Список:\n{0}'.format(
            '\n'.join(['/pe' + x.replace('_', ' ') for x in sorted(pe_db)[:-1]]) +
            '\n/ab ' + sorted(pe_db)[-1]))

        keyboard_hider = types.ReplyKeyboardRemove()

    elif message.text == '1.Effortless English':

        smes(message,
             'Выребите уровень:\nLevel 1\nLevel 2\nLevel 3\
             \nLevel 4\nИли загрузите:\n/mst mini_story_transcripts.pdf\
             \n/wg welcome_guide.pdf')

        bot.send_message(message.chat.id, "Выберите уровень:",
                         reply_markup=markup_generator(markup_list1))
        keyboard_hider = types.ReplyKeyboardRemove()

    else: response_catcher(message)




def response_catcher(message):

    level_1 = (('\n/eel'.join(sorted(list(
        ee_db.get('Effortless English').get(
            'Level 1')))).replace('_', ' '))).replace('.', 'ep')

    level_2 = (('\n/eel'.join(sorted(list(
        ee_db.get('Effortless English').get(
            'Level 2')))).replace('_', ' '))).replace('.', 'ep')

    level_3 = (('\n/eel'.join(natsorted(list(
        ee_db.get('Effortless English').get(
            'Level 3')))).replace('_', ' '))).replace('.', 'ep')

    level_4 = '4hi Hitch Intro\n/eel4bh1 Bonus Hitch 1' \
              '\n/eel4bh2 Bonus Hitch 2\n/eel4bh3 Bonus Hitch 3'

    level_dict = {
        markup_list1[0]: level_1,
        markup_list1[1]: level_2,
        markup_list1[2]: level_3,
        markup_list1[3]: level_4
    }

    if message.text in markup_list1:
        bot.send_message(message.chat.id, "Выберите историю:\n/eel{}".format(level_dict[message.text]))




if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))