import json
from natsort import natsorted
import pymongo
import natsort
import pdb

connection = pymongo.MongoClient('localhost')
db = connection['HogeBotDB']
ee_db = json.load(open('ee_database.json'))
pe_db = json.load(open('pe_database.json'))
message_list = [['/eel1ep' + str(x) for x in range(1, 9)],
           ['/eel2ep' + str(x) for x in range(1, 9)],
           ['/eel3ep' + str(x) for x in range(1, 21)],
           ['/eel4hi', '/eel4bh1', '/eel4bh2', '/eel4bh3', '/mst', '/wg']]
messages = []
for i in message_list:
    messages.extend(i)
command = [['/pe0' + str(x) for x in range(1, 10)],['/pe' + str(x)
                                                   for x in range(10, 31)]]
pe_command_list = []

for i in command: pe_command_list.extend(i) # объединение списков команд
print(pe_command_list)

def update_db(command, filename):

    db['ee_dump'].update({'_id': filename}, {'$set':{'command': command}})

def response_generator(message):
    '''
    Генератор ответов на запросы со слэшем. Желательно
    записать в "базу" чтобы не генерировать каждый раз.
    '''

        #   ['eel4hi', 'eel4bh1', 'eel4bh2', 'eel4bh3', 'mst', 'wg', 'ab']]
    if message[:5] == '/eel4':

        if message == '/eel4hi':

            for file in ee_db['ee_dump']['Level 4']['Hitch Intro']:

                update_db('/eel4hi', file )


        elif message == '/eel4bh1':

            for file in ee_db['ee_dump']['Level 4']['4_Bonus_Hitch_1']:

                update_db('/eel4h1', file )

        elif message == '/eel4bh2':

            for file in ee_db['ee_dump']['Level 4']['4_Bonus_Hitch_2']:

                update_db('/eel4h2', file )

        elif message == '/eel4bh3':

            for file in ee_db['ee_dump']['Level 4']['4_Bonus_Hitch_3']:

                update_db('/eel4h3', file )


    elif message[:3] == '/ee':
        # Получение уровня из сообщения постыдным способом
        dic_number = message.split('eel')[1].split('ep')[0]
        # Получение темы из сообщения постыдным способом
        theme_number = message.split('eel')[1].split('ep')[1]
        # Получение списка уровней из ключей базы
        ee_keylist = natsorted(list(ee_db['ee_dump']))[0:4]
        # Получение ключа уровня для вызова из словаря
        ee_levelkey = ee_keylist[int(dic_number) - 1]
        # Получение списка из значения словаря нужного уровня
        ee_themekey = natsorted(list(ee_db['ee_dump'][ee_levelkey]))
        # Целевой словарь с ид файлов
        target_dic = ee_db['ee_dump'][ee_levelkey][ee_themekey[
            int(theme_number) - 1]]

        for file in target_dic:

            update_db(message, file)

    elif message[:3] == '/pe':

        # Схожая с предыдущим схема, базы делал в разное время и
        # разными подходами, логика немного различна
        pe_story_number = int(message[-2:])
        pe_keylist = natsorted(list(pe_db))
        pe_storykey = pe_keylist[pe_story_number - 1]

        for file in pe_db[pe_storykey]['audio']:
            update_db(message, file)

        for file in pe_db[pe_storykey]['documents']:
            update_db(message, file)

    elif message == '/mst':
        update_db(message, 'mini_story_transcripts.pdf')

    elif message == '/wg':
        update_db(message,'welcome_guide.pdf')

    elif message == '/ab':

        for file in pe_db['Commentary Audio Bonuses']['audio']:
            update_db(message, file)

        for file in pe_db['Commentary Audio Bonuses']['documents']:
            update_db(message, file)



#pdb.set_trace()
#for point in pe_command_list:
a = response_generator('/ab')
