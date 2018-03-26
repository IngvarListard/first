# -*- coding: utf-8 -*-
import telebot
import config
import json
import os
import time

bot = telebot.TeleBot(config.token)
files = '/home/ingvar/PycharmProjects/HogeBot/audio/'

#def dir_check(message, bd): # Функция для рекурсивного открытия папок до второго уровня, и отправки из них данных


bd = dict()

@bot.message_handler(commands=['test'])
def find_file_ids(message):

    for file in os.listdir(files):
        print("Обработка списка файлов")

        if os.path.isdir(files+file+'/') is True: # Проверка является ли объект директорией, если да, то
            print("Обработка содержания папок")

            for subfile in os.listdir(files + file + '/'): # Для каждого файла в этой директории
                print("Сортировка списка файлов")

                if subfile.split('.')[-1] == 'mp3': # В зависимости от его формата, выполняется код отправки в телегу
                    print("Отправка аудиозаписи")

                    f = open(files + file + '/' + subfile, 'rb') # Открытие файлов перед отправкой
                    msg = bot.send_audio(message.chat.id, f) # Объявление переменной для отправки аудио
                    bot.send_message(message.chat.id, msg.audio.file_id, reply_to_message_id=msg.message_id) # Получение id отправленного файла. Отправляется как reply на сообщение с файлом
                    theme = file # Для наглядности задачи file - название папки в которой содержатся обрабатываемые файлы
                    bd.setdefault(theme, dict(audio=dict(), documents=dict())) # Создание структуры базы
                    middle_dic = bd[theme]['audio'] # Словарь с аудиозаписями
                    middle_dic[subfile] = msg.audio.file_id # Дополнениие словаря с аудио


                elif subfile.split('.')[-1] == 'pdf':
                    print("Отправка документа")

                    f = open(files + file + '/' + subfile, 'rb')
                    msg = bot.send_document(message.chat.id, f)
                    bot.send_message(message.chat.id, msg.document.file_id, reply_to_message_id=msg.message_id)
                    theme = file
                    bd.setdefault(theme, dict(audio=dict(), documents=dict()))
                    middle_dic = bd[theme]['documents']
                    middle_dic[subfile] = msg.document.file_id

                else:
                    print(subfile+' не поддерживается.')
    print("Окончание. Запись в файл")
    with open("database.json", "w", encoding="utf-8") as file:
        json.dump(bd, file)

    time.sleep(3)




if __name__ == '__main__':
    bot.polling(none_stop=True)