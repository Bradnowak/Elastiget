from os import system, name
import json
from time import sleep

print("Pulling down prerequisite modules...")
system("pip3 install elasticsearch --user")
system("pip3 install tqdm --user")

from elasticsearch import Elasticsearch


connected = False
#ip = '192.168.1.172'
#port = '9200'

def clear():
    # for windows
    if name == 'nt':
        _ = system('cls')

        # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')

def testconnection(es):
    global connected
    test_connection = es.ping()
    if test_connection:
        connected = True
    else:
        print("Connection failed...")
        connected = False


def connect():
    global ip
    global port
    ip = input("Input Elastic cluster IP: ")
    port = input("Input port: ")
    conn = Elasticsearch([{'host': ip, 'port': port}])
    testconnection(conn)
    return conn


def search(es, index_name, topic, query):
    if topic == None and query == None:
        search_q = '{ "size": 10000, "query": { "match_all": {}}}'
        res = es.search(index=index_name, body=search_q)
    else:
        search_q = '{ "size": 10000, "query": { "match": { "' + topic + '": { "query": "' + query + '" } } } }'
        res = es.search(index=index_name, body=search_q)
    return res


def get_index(es):
    print("\nPlease select an index to search.  To search all indices input \'*\'\n")

    keys = (es.indices.get_alias('*').keys())

    keylist = []
    for key in keys:
        keylist.append(key)
    keylist.sort()

    for i, key in enumerate(keylist):
        print(str(i) + '.' + str(key))

    num = input("\nIndex number: ")

    if num == '*':
        return '*'

    try:
        num = int(num)
    except ValueError:
        print("Please select an integer.")
        get_index(es)

    if num > len(keylist) or num < 0:
        print("Invalid selection.")
        get_index(es)

    index_val = keylist[num]

    return index_val


def main_menu(es):
    _topic = None
    _q_string = None
    _index = None
    menu = []
    menu.append("Get specific logs type by event_type")
    menu.append("Get specific logs by tags")
    menu.append("Get specific logs by custom field")
    menu.append("Get all documents")
    menu.append("Exit")

    for entry in range(len(menu)):
        print("[" + str(entry) + "]", menu[entry])
    selection = input("\nPlease Select: ")

    if selection == '0':
        _topic = "event_type"
        _q_string = input("Input event_type: ")
        _index = get_index(es)
    elif selection == '1':
        _topic = "tags"
        _q_string = input("Input tag: ")
        _index = get_index(es)
    elif selection == '2':
        _topic = input("Custom field: ")
        _q_string = input("Query string: ")
        _index = get_index(es)
    elif selection == '3':
        _index = get_index(es)
    elif selection == '4':
        exit()
    else:
        print("Invalid input.")
        sleep(2)
        main_menu(es)

    return _topic, _q_string, _index


def save():
    ans = input("Save file to disk? ")
    if ans== "yes" or ans =="y":
        f_name = input("Input file name: ")
        if ".json" in f_name:
            f = open(f_name, "w")
            f.write(text)
            f.close()
        else:
            f = open(f_name + ".json", "w")
            f.write(text)
            f.close()
    elif ans == "no" or ans == "n":
        pass
    else:
        print("Please type yes or no.")
        save()


if __name__ == "__main__":

    es_obj = connect()
    testconnection(es_obj)

    while connected:
        print("\n" + "*" * 10 + "Connected to elastic cluster at: " + ip + " via port: " + port + "*" * 10 + "\n")
        topic, q_string, index = main_menu(es_obj)
        query = search(es_obj, index, topic, q_string)
        text = (json.dumps(query, indent=4, sort_keys=True))
        print(text)
        save()

    print("Disconnected from elastic cluster")
