import json
import pymongo

connection = pymongo.MongoClient('localhost')
db = connection['HogeBotDB']
edb = json.load(open('pe_database.json'))
new_db = dict()

def trans(database, parent='Power English'):

    for node in database:

        result = dict()
        # Если нод -- ключ словаря, то выполняем код
        if (node == 'audio') or (node == 'documents'):

            trans(database[node], parent=parent)

        elif (database.get(node, False) != False) and (
                    type(database.get(node)) is dict):

#            list1 = list(database[node]['audio'])
#            list2 = list(database[node]['documents'])
#            list1.extend(list2)
#
           # print(list1)
           # result = {"_id": node, "children": list1}
           # print(result)
            db['Power English'].update({'_id': node}, {'$set': {'parent': parent}})
            trans(database[node], node)

        elif database.get(node, False) == False:

            continue

        elif type(database.get(node)) is str:

            #key = dict(node = database[node].get)
            #result = {"_id": node, "key": database[node]}
            db['Power English'].update({'_id': node}, {'$set': {'parent': parent}})

trans(edb)
