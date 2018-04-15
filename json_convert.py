import json
import pymongo

connection = pymongo.MongoClient('localhost')
db = connection['HogeBotDB']
edb = json.load(open('ee_database.json'))

def trans(database, parent='Effortless English'):
    """
    Импорт базы EE из json в MongoDB.
    На данный момент не импорт, а добавление к каждой записи 'parent'
    """
    for node in database:

        result = dict()
        # Если нод -- ключ словаря (папка), то выполняем код
        if (database.get(node, False) != False) and (type(database.get(node))
             is dict):
            # под комментами старые значения result, которые служили аргументом
            # функции db.insert_one. Пришлось заменить, т.к. функция update
            # принимает минимум два аргумента
            #result = {'_id': node, '$set': {'parent': parent, 'children': list(database.get(node))}}
            #result = {"_id": node, "parent": parent, "children": list(database.get(node))}
            db['Effortless English'].update({'_id': node}, {'$set': {'parent': parent}})
            trans(database[node], node)

        elif database.get(node, False) == False:

            continue

        elif type(database.get(node)) is str:

            #key = dict(node = database[node].get)
            #result = {"_id": node, "key": database[node], "parent": parent}
            db['Effortless English'].update({'_id': node}, {'$set': {'parent': parent}})
trans(edb)

