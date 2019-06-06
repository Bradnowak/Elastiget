import json
from os import system, name
from elasticsearch import Elasticsearch

connected = False

def clear():
    if name == 'nt':
        _ = system('cls')
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


def process_hits(hits):
    hits_list = []
    for item in hits:
        hits_list.append((json.dumps(item, indent=2)))
    return hits

def search(es, index_name, topic, query):
    hits = []
    if topic is None and query is None:
        search_q = '{ "size": 10000, "query": { "match_all": {}}}'
    else:
        search_q = '{ "size": 10000, "query": { "match": { "' + topic + '": { "query": "' + query + '" } } } }'

    res = es.search(index=index_name, body=search_q, scroll='5m')
    sid = res['_scroll_id']
    scroll_size = res['hits']['total']
    print("Scroll size: " + str(scroll_size))

    while scroll_size > 0:
        print('Scrolling...')
        res = es.scroll(scroll_id=sid, scroll='5m')
        sid = res['_scroll_id']
        scroll_size = len(res['hits']['hits'])
        print("Scroll size: " + str(scroll_size))
        hits.append(process_hits(res['hits']['hits']))
    return hits


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
        main_menu(es)

    return _topic, _q_string, _index


def save(output):
    ans = input("Save to disk? ")
    if ans == "yes" or ans == "y":
        ans2 = input("[0] Single file or [1] Multiple files?")
        while ans2 != '0' and ans2 != '1':
            ans2 = input("Invalid answer.  [0] Single file or [1] Multiple files?")

        if ans2 == '0':
            f_name = input("Input file name: ")

            if ".json" in f_name:
                f = open(f_name, "a+")
            else:
                f = open(f_name + ".json", "a+")

            for out_list in output:
                for in_list in out_list:
                    f.write(json.dumps(in_list['_source'], indent=4))
                    f.write('\n')
            f.close()

        elif ans2 == '1':
            f_name = input("Input base file name: ")
            i = 1

            for out_list in output:
                for in_list in out_list:
                    f = open(f_name + str(i) + '.json', 'w+')
                    f.write(json.dumps(in_list['_source'], indent=4))
                    i += 1
                    f.close()



    elif ans == "no" or ans == "n":
        pass
    else:
        print("Please type yes or no.")
        save(output)



if __name__ == "__main__":

    es_obj = connect()
    testconnection(es_obj)

    while connected:
        print("\n" + "*" * 10 + "Connected to elastic cluster at: " + ip + " via port: " + port + "*" * 10 + "\n")
        topic, q_string, index = main_menu(es_obj)
        hits = search(es_obj, index, topic, q_string)
        save(hits)

    print("Disconnected from elastic cluster")
