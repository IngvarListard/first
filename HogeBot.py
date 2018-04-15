# -*- coding: utf-8 -*-
import config
import telebot
import pymongo
from natsort import natsorted

#БД Подключение к
connection = pymongo.MongoClient('localhost')
db = connection['HogeBotDB']
# Описание бота
bot = telebot.TeleBot(config.token)
types = telebot.types
# list of levels for EE course
markup_list1 = ['Level 1', 'Level 2', 'Level 3', 'Level 4']
# list of levels for pimsleur course
pimsleur_markup = [
    'Pimsleur English for Russian Speakers I',
    'Pimsleur English for Russian Speakers II',
    'Pimsleur English for Russian Speakers III',
    'Reading Lessons']
# Legacy functionality. Commands were instead of inline keyboard
command = [['eel1ep' + str(x) for x in range(1, 9)],
           ['eel2ep' + str(x) for x in range(1, 9)],
           ['eel3ep' + str(x) for x in range(1, 21)],
           ['eel4hi', 'eel4h1', 'eel4h2', 'eel4h3', 'mst', 'wg']]
command_list = []
for i in command: command_list.extend(i)  # объединение списков команд
command = [['pe0' + str(x) for x in range(1, 10)],['pe' + str(x)
                                                  for x in range(10, 31)]]
pe_command_list = []
for i in command: pe_command_list.extend(i)  # объединение списков команд
pe_command_list.append('ab')

def pimsleur_theme_generator(lesson):
    list_of_dicks = {}
    parent = db['pimsleur'].find_one({'_id': lesson})['parent']
    lessons_list = db['pimsleur'].find_one({'_id': parent})['children']
    lessons_list = natsorted(lessons_list)

    for i in lessons_list:
        if len(list_of_dicks) == 30:
            break

        else:
            key, val = i, lessons_list[lessons_list.index(i) + 30]
            list_of_dicks[key] = val

    key_list = []
    key1 = db['pimsleur'].find_one({'_id': lesson})['key']
    key2 = db['pimsleur'].find_one({'_id': list_of_dicks[lesson]})['key']
    key_list.append(key1)
    key_list.append(key2)

    return key_list, lessons_list, parent

def last_user_theme_to_db(theme_list, chat_id, theme, collection):
    """Writes last and new user's course's theme to db, returns next theme"""
    next_theme_index = theme_list.index(theme) + 1

    try:
        next_theme = theme_list[next_theme_index]

    except IndexError:
        next_theme = None

    db['users'].save({'_id': chat_id, 'collection': collection,
    'current_theme': theme, 'next_theme': next_theme})

    return next_theme

def inline_markup_generator(markup_list, course, position=[0,10], parent=None):
    """
    Генератор inline кнопок с коллбэком. Для обычных "тем курсов" в коллбэке
    всего две позиции разделённые знаком '%':
    [0] - имя темы; [1] - имя коллекции в БД;
    Если кнопка является стрелкой то добавляется:
    [0] - 'False'; [1] - имя коллекции в БД; [2] - parent for nested courses;
    [3] - текущая позиция: 10 если [0:10], 20 если [10:20]. Берётся последняя
    цифра списка; [4] - направление стрелки: 'l' - left, 'r' - right.
    """
    keyboard = types.InlineKeyboardMarkup()  # генератор инлайн клавиатуры
    kb_button = types.InlineKeyboardButton  # генератор кнопок

    # generation inline kb for next position
    if position[0] > 0:

        for theme in markup_list[position[0]:position[1]]:
            keyboard.row(
            kb_button(text=theme, callback_data='{}%{}'.format(theme, course)))
        # arrows
        keyboard.row(
        kb_button(
        text='\U00002B05',callback_data='{}%{}%{}%{}%{}'.format('False',course,
        parent,position[1],'l')),
        kb_button(
        text='\U000027A1',callback_data='{}%{}%{}%{}%{}'.format('False',course,
        parent,position[1],'r')))

    # если список из 10 или менее элементов, то кнопки навигации не добавляются
    elif len(markup_list) <= 10:

        for theme in markup_list:
            keyboard.row(kb_button(text=theme, callback_data='{}%{}'.format(
            theme, course)))

    # если больше -- добавляются
    elif len(markup_list) > 10:

        for theme in markup_list[:10]:
            keyboard.row(
            kb_button(text=theme, callback_data='{}%{}'.format(theme, course)))
        # стрелочки с коллбэком в виде инфы о положении и направлении
        keyboard.row(
        kb_button(
        text=u'\U00002B05',callback_data='{}%{}%{}%{}%{}'.format('False'
        ,course,parent,10,'l')),
        kb_button(
        text=u'\U000027A1',callback_data='{}%{}%{}%{}%{}'.format('False',
        course,parent,10,'r')))

    return keyboard

def theme_list_generator(collection, theme=None, parent=None):
    """
    В попытках навести хоть какой-то порядок, генератор списков тем\курсов\етц
    из базы, для запросов по имени в коллбэк. Попытка в универсальность.
    """

    if collection == 'pimsleur':
            print(parent)
            print(theme)
            query = db[collection].find_one({'_id': parent})['children']
            dirty_list = natsorted(query)
            theme_list = dirty_list[:30]
    # Necessary condition for processing EE with nested levels\dirs
    elif theme is None and ((parent == None) or (parent=='None')):
        query = db[collection].find({'parent': collection, 'children': {
            '$exists': 1}}, {'_id': 1}).sort('_id')
        theme_list = []

        for i in query:
            theme_list.append(i['_id'])

    # attempt to fix problem with nested dirs for EE and maybe others
    elif (parent is not None) and (parent != 'None'):
        query = db[collection].find_one({'_id': parent})
        theme_list = query['children']

    else:
        # get parent for getting 'children'(which is theme_list)
        parent = db[collection].find_one({'_id': theme},{
            '_id': 0, 'parent': 1})['parent']

        if parent not in db.collection_names():
            theme_list = db[collection].find_one({'_id': parent}, {
                    '_id':0, 'children': 1})['children']

        else:
            query = db[collection].find({'parent': collection, 'children': {
                '$exists': 1}}, {'_id': 1}).sort('_id')
            theme_list = []

            for i in query:
                theme_list.append(i['_id'])

    return natsorted(theme_list)

def ee_level_list_generator(message):
    """
    Обработка текстовых запросов по уровню.Принимает на вход номер уровня
    Effortless English, отправляет в чат инлайн список с содержимым level.
    """
    query = db['Effortless English'].find_one({
        '_id': message.text, 'children': {'$exists': 1}})
    list_of_stories_in_level = natsorted(query['children'])
    bot.send_message(message.chat.id, 'Выберите тему курса',
        reply_markup = inline_markup_generator(list_of_stories_in_level,
        'Effortless English', parent=message.text))

def smes(message, text): # Облегчаем жизнь отправки сообщений
    """Legacy trash."""
    bot.send_message(message.chat.id, text)

def markup_generator(markup_list):
    """Get list of button. Reurns keyboard"""
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,
        resize_keyboard=True)

    for item in markup_list:
        markup.add(item)

    return markup

@bot.message_handler(commands=['start','help'])
def help_request(message):
    """Зохват /start, /help."""
    smes(message, 'Добро пожаловать на аудиокурсы Английского языка'
                  ' by A.J. Hoge.\nВведите /learn чтобы приступить к обучению')

@bot.message_handler(commands=['learn'])
def learn(message):
    """Зохват для вывода списка курсов."""

    smes(message,
        'Пожалуйста выберите курс, который хотите изучить'
        '\nEffortless English\nPower English\n'
        'Pimsleur English for Russian Speakers')

    markup_list = ['Pimsleur English for Russian Speakers',
    'Effortless English', 'Power English']
    bot.send_message(message.chat.id, "Выберите курс:",
                     reply_markup=markup_generator(markup_list))

@bot.message_handler(commands=command_list)
def ee_response_generator(message):
    """Response generator for commands with '/' for EE course."""
    for file in db['Effortless English'].find({'command': message.text}):
        bot.send_document(message.chat.id, file['key'])

@bot.message_handler(commands=pe_command_list)
def pe_response_generator(message):
    """Response generator for commands with '/' for PE course."""
    for file in db['Power English'].find({'command': message.text}):
        bot.send_document(message.chat.id, file['key'])

@bot.message_handler(func=lambda message: True, content_types=['text'])
def simple_text_catcher(message):
    """Response generator for simple text query"""

    if message.text == 'Power English':
        theme_list = theme_list_generator(message.text)
        inline_kb = inline_markup_generator(theme_list, 'Power English')
        # Отправка сообщения со списком
        bot.send_message(
        message.chat.id, 'Выберите тему курса', reply_markup = inline_kb)

    elif message.text == 'Effortless English':
        bot.send_message(message.chat.id,
             'Выребите уровень:\nLevel 1\nLevel 2\nLevel 3\
             \nLevel 4\nИли загрузите:\n/mst mini_story_transcripts.pdf\
             \n/wg welcome_guide.pdf')
        bot.send_message(message.chat.id, "Выберите уровень:",
                         reply_markup=markup_generator(markup_list1))
        keyboard_hider = types.ReplyKeyboardRemove()

    elif message.text == 'Следующая тема':
        query = db['users'].find_one({'_id': message.chat.id})
        next_theme = db[query['collection']].find_one({
            '_id':query['next_theme']})

        if next_theme is None:
            bot.send_message(message.chat.id, 'Это была последняя тема курса. '
                'Вы можете выбрать другой курс запустив /learn')

        else:
            bot.send_message(message.chat.id, next_theme['_id'])

            if query['collection'] == 'pimsleur':
                lesson, theme_list, parent_1 = pimsleur_theme_generator(
                    query['next_theme'])

                for key in lesson:
                    bot.send_document(message.chat.id, key)

            else:
                theme_list = theme_list_generator(
                    query['collection'], query['current_theme'])

                for children in next_theme['children']:
                    bot.send_document(message.chat.id,
                    db[query['collection']].find_one({'_id': children})['key'])

            last_user_theme_to_db(theme_list, message.chat.id,
                next_theme['_id'],query['collection'])

    elif message.text.split(' ')[0] == 'Level':
        ee_level_list_generator(message)

    elif message.text == 'Список тем текущего курса':
        query = db['users'].find_one({'_id': message.chat.id})

        if query['collection'] == 'pimsleur':
            lesson, theme_list, parent = pimsleur_theme_generator(
                query['current_theme'])

        else:
            theme_list = theme_list_generator(
                query['collection'], theme=query['current_theme'])
        parent = db[query['collection']].find_one(
            {'_id': query['current_theme']})['parent']

        inline_kb = inline_markup_generator(
            theme_list, query['collection'], parent=parent)
        bot.send_message(message.chat.id,
            'Список тем текущего курса:', reply_markup=inline_kb)

    elif message.text == 'Pimsleur English for Russian Speakers':
        kb_markup = markup_generator(pimsleur_markup)
        bot.send_message(message.chat.id, text='Выберите сложность курса',
            reply_markup=kb_markup)

    elif message.text in pimsleur_markup:
        theme_list = natsorted(theme_list_generator('pimsleur',
            parent=message.text))[:30]
        inline_kb = inline_markup_generator(theme_list, 'pimsleur',
            parent=message.text)
        bot.send_message(
            message.chat.id, 'Выберите тему курса', reply_markup = inline_kb)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    """
    Перехватчик колбэка от кнопок. На данный момент коллбэк приходит в виде
    строки с пятью параметрами разделёнными символом '%'. Шпаргалка:
    [0] - название темы или 'False' если кнопка является стрелкой;
    [1] - имя коллекции рассматриваемого курса\темы;
    [2] - parent for nested courses
    [3] - позиция. Если 10 то позиция [0:10], если 20, то [10:20] и т.д.;
    [4] - 'r' или 'l' - стрелка впарво или влево.
    """
    call_list = call.data.split('%')  # создание списка удобного для обработки

    if call_list[0] == 'False':

        if call_list[4] == 'l':
            x = int(call_list[3]) - 20
            y = int(call_list[3]) - 10
            pos = [x, y]

            if x < 0:
                bot.answer_callback_query(call.id,
                    text ='Вы достигли начала списка', show_alert=False)

            if x >= 0:
                theme_list = theme_list_generator(
                    call_list[1], parent=call_list[2])
                inline_kb = inline_markup_generator(
                    theme_list, call_list[1],
                position = pos, parent=call_list[2])
                bot.edit_message_text(chat_id = call.message.chat.id,
                    message_id=call.message.message_id,
                text ='Выберите тему курса', reply_markup=inline_kb)

        elif call_list[4] == 'r':
            x = int(call_list[3])
            y = int(call_list[3]) + 10
            pos = [x, y]
            theme_list = theme_list_generator(call_list[1],
                parent=call_list[2])

            if len(theme_list[x:y])==0:
                bot.answer_callback_query(call.id,
                    text='Вы достигли конца списка', show_alert=False)

            else:
                inline_kb = inline_markup_generator(theme_list, call_list[1],
                    position=pos, parent=call_list[2])
                bot.edit_message_text(chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text = 'Выберите тему курса', reply_markup=inline_kb)

    else:
        chat_id = call.message.chat.id
        buttons_list = ['Следующая тема', 'Список тем текущего курса',
            '/learn']
        a = markup_generator(buttons_list)


        if call_list[1] == 'pimsleur':
            key_list, theme_list, parent_2 = pimsleur_theme_generator(
                call_list[0])
            bot.answer_callback_query(call.id, text="Отправка файлов",
                show_alert=False)
            next_theme = last_user_theme_to_db(theme_list[:30], chat_id,
                call_list[0], call_list[1])

            for key in key_list:
                bot.send_document(chat_id, key)
        else:
            files = db[call_list[1]].find_one(
                {'_id': call_list[0]})['children']
            theme_list = theme_list_generator(call_list[1], call_list[0])
            next_theme = last_user_theme_to_db(
                theme_list, chat_id, call_list[0], call_list[1])

            for file in files:
                bot.answer_callback_query(call.id, text="Отправка файлов",
                    show_alert=False)
                bot.send_document(call.message.chat.id,
                    db[call_list[1]].find_one({'_id': file})['key'])

        bot.send_message(chat_id, 'Вы также можете выбрать следующую тему, '
        'если откроете клавиатуру', reply_markup = a)
        keyboard_hider = types.ReplyKeyboardRemove()

if __name__ == '__main__':
     bot.polling(none_stop=True)
