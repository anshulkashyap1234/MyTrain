from mytrain.setting import mydb
from scripts.fetch_stations import main as station_info_train_no
from pymongo import UpdateOne



def database_server(data: list, request_id) -> tuple:
    for i in data:
        key = {'train_number': i.get('train_number')}
        mydb.search_result.find_one_and_update(key, {'$set': i, "$addToSet": {
                                               "request_id": {"$each": [request_id]}}}, upsert=True)
    return int(1), {'status': 'successfully update and upsert data in database'}


def get_train(toDest, fromDest) -> (list, None):
    print(toDest, fromDest)
    request_id = mydb.keywordsearch.find_one(
        {'toDest': toDest, 'fromDest': fromDest})
    print(request_id)
    if request_id != None:
        request_id = dict(request_id)
        data = mydb.search_result.find(
            {'request_id': request_id.get('request_id')}, {"_id": 0})
        dataset = [i for i in data]
        if len(dataset) > 0:
            return dataset
    return None


def keywordsearch(toDest, fromDest, reqest_id):
    mydb.keywordsearch.insert_one(
        {'toDest': toDest, 'fromDest': fromDest, 'request_id': reqest_id})


def get_details(train_no):
    data = mydb.search_result.find_one({'train_number': train_no})
    if data != None:
        data = dict(data)
        return data
    return None


def user_singin(dic: dict):
    mydb.user_data.insert_one(dic)


def get_user_name(client_id):
    user = mydb.user_data.find_one({'client_id': client_id})

    return dict(user).get('name')

def get_user_id(email,password):
    user = mydb.user_data.find_one({'email': email,'password':password})
    print(user)
    if user==None:
        return None
    return dict(user).get('client_id')


def store_train_data(new_stations):
    update_operations = [
        UpdateOne({'station_name': station['station_name']}, {'$set': station}, upsert=True)
        for station in new_stations
    ]
    data=mydb.traindatabase.bulk_write(update_operations)
    return True


def store_station_train(train_no,stations):
        data=mydb.stations_train.find_one_and_update({'train_no':train_no},{'$set':{'stations':stations}},upsert=True)
        return True

def check_train_no_exists(train_no):
    train_info=mydb.stations_train.find_one({'train_no':train_no})
    if train_info:
        return train_info.get('stations')
    else:
        stations=station_info_train_no(train_no)
        if all(stations):
            store_station_train(train_no,stations)
        else:
            return None,None
        return stations