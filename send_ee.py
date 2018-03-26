# The code for creating a nested dictionary was taken from: https://github.com/ActiveState/code
# Recipe for creating the 'sender' was taken from: https://groosha.gitbooks.io/telegram-bot-lessons/content/chapter2.html

import os
from functools import reduce
import config
import json
import telebot
import time



bot = telebot.TeleBot(config.token)
rootdir = '/home/ingvar/PycharmProjects/HogeBot/audio/'
#path


def send_file(message, path, file):

    if file.split('.')[-1] == 'mp3':  # В зависимости от его формата, выполняется код отправки в телегу
        print("Отправка аудиозаписи")

        f = open(os.path.join(path, file), 'rb')  # Открытие файлов перед отправкой
        msg = bot.send_audio(message.chat.id, f)  # Объявление переменной для отправки аудио
        bot.send_message(message.chat.id, msg.audio.file_id,
                         reply_to_message_id=msg.message_id)  # Получение id отправленного файла. Отправляется как reply на сообщение с файлом
        id = msg.audio.file_id


    elif file.split('.')[-1] == 'pdf':
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
    rootdir = '/home/ingvar/PycharmProjects/HogeBot/audio/Effortless English/'
    dir = {} # добавление словаря в который будет записываться дерево
    rootdir = rootdir.rstrip(os.sep) # удаление '/' в конце строки, для упрощения дальнейших операций
    # с помощью этой переменной будут искаться разделители адреса os.sep - '/'
    # и последний отделяться в качестве названия для каталога.
    # start вероятно из-за определения переменной как начало дерева; корневой каталог
    start = rootdir.rfind(os.sep) + 1

    for path, dirs, files in os.walk(rootdir): # обход пути, обработка и запись в словарь

        # print(files)
        # files = b
        # Парсинг названия обрабатываемой на конкретном круге цикла
        # директории из полного пути с помощью переменной start
        # (т.е. включает в себя только то, что идёт после корневого каталога, включая оный)
        folders = path[start:].split(os.sep)
        d = dict.fromkeys(files) # создание словаря subdir из названий папок files
        subdir = dict()
        for key in d:
            subdir[key] = send_file(message, path, key)
        parent = reduce(dict.get, folders[:-1], dir) # при первом проходе добавляет всё содержимое списка folders без последнего элемента в словарь, как вложенный словарь
        parent[folders[-1]] = subdir

    print("Окончание. Запись в файл")
    with open("ee_database.json", "w", encoding="utf-8") as file:
        json.dump(dir, file)

    time.sleep(3)

if __name__ == '__main__':
    bot.polling(none_stop=True)