
# Отправка вложенных документов и аудио в телегу, и запись всего этого в базу
import os
from functools import reduce
import config
import json
import telebot
import time
import pymongo

connection = pymongo.MongoClient('localhost')
db = connection['HogeBotDB']

bot = telebot.TeleBot(config.token)
rootdir = '/home/ingvar/Downloads/lingvo/Pimsleur English for Russian Speakers/'
rootdir = rootdir.rstrip(os.sep)

def send_file(message, path, file):

    if file.split('.')[-1] == 'mp3':  # В зависимости от его формата, выполняется код отправки в телегу
        print("Отправка аудиозаписи")

        f = open(os.path.join(path, file), 'rb')  # Открытие файлов перед отправкой
        msg = bot.send_audio(message.chat.id, f)  # Объявление переменной для отправки аудио
        bot.send_message(message.chat.id, msg.audio.file_id,
                         reply_to_message_id=msg.message_id)  # Получение id отправленного файла. Отправляется как reply на сообщение с файлом
        id = msg.audio.file_id


    elif (file.split('.')[-1] == 'pdf') or (file.split('.')[-1] == 'doc'):
        print("Отправка документа")

        f = open(os.path.join(path, file), 'rb')
        msg = bot.send_document(message.chat.id, f)
        bot.send_message(message.chat.id, msg.document.file_id, reply_to_message_id=msg.message_id)
        id = msg.document.file_id

    else:
        print(file + ' не поддерживается.')
        id = None

    return id



@bot.message_handler(commands=['test'])
def get_directory_structure(message):
    """
    Creates a nested dictionary that represents the folder structure of rootdir
    """
    for path, dirs, files in os.walk(rootdir):

#        for file in files:
#            key = send_file(message, path, file)
#            db['pimsleur'].save({'_id': file, 'parent': path.split(os.sep)[-1],
#                'key': key})
#
        for dir in dirs:
            children = os.listdir(os.path.join(path, dir))
            children.extend(files)
            db['pimsleur'].save({'_id': dir, 'parent': path.split(os.sep)[-1],
                'children': children})

    print('Всё кончено')
    time.sleep(3)

if __name__ == '__main__':
    bot.polling(none_stop=True)
