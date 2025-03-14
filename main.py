vehicles_key = "p7vHH37UlR6benMiGojWaaN33Fru9hIM4czn68El"
trips_key = "A6s7YxmFbw1c5XtSgSDBq8UPX9jat0Dp3CdbOk8q"
routes_key = "inmMFTMKMW2X5kGdJs8Yz15RDjqsesRp5gVmiqem"
stops_key = "0MM3zea8jl5aAJlJvP0bH6GP4a8ovtZ2a67T4YQM"
stop_times_key = "YAt2zxijuE9OvO0lHZEiI4ipasD3h2O28ADLPLtr"

import requests
import json
import mysql.connector
import time


# start_time=time.time()

# end_time=time.time()
# print(f'TOOK:{end_time-start_time} seconds.')

# *-----JSON-REQUESTS/FORMATTING------------------------

def jprint(json_data):
    print(json.dumps(json_data, indent=4))


def request_vehicle_info(api_key):
    url = "https://api.tranzy.dev/v1/opendata/vehicles"
    headers = {
        "X-Agency-Id": "4",
        "Accept": "application/json",
        "X-API-KEY": api_key
    }

    response = requests.get(url, headers=headers)
    return json.loads(response.text)


def filter_by_vehicle_type(json_data, type):
    if json_data == None:
        return None

    filtered_json_data = []
    for data_pack in json_data:

        if data_pack['vehicle_type'] == type:
            filtered_json_data.append(data_pack)

    return filtered_json_data


def format_vehicle_data(json_data):
    keys_to_keep = ['id', 'vehicle_type', 'route_id', 'trip_id', 'latitude', 'longitude', 'speed',
                    'wheelchair_accessible']
    formated_data = []

    for data_pack in json_data:
        if data_pack['trip_id'] == 'undefined_0':
            continue

        formated_data_pack = {key: data_pack[key] for key in keys_to_keep if key in data_pack}
        formated_data.append(formated_data_pack)

    return formated_data


def request_routes_info(api_key):
    url = "https://api.tranzy.dev/v1/opendata/routes"
    headers = {
        "X-Agency-Id": "4",
        "Accept": "application/json",
        "X-API-KEY": api_key
    }

    response = requests.get(url, headers=headers)
    return json.loads(response.text)


def format_routes_data(json_data):
    keys_to_keep = ['route_id', 'route_short_name', 'route_long_name', 'route_type']
    formatted_data = []
    for data_pack in json_data:
        formatted_data_pack = {key: data_pack[key] for key in keys_to_keep if key in data_pack}
        formatted_data.append(formatted_data_pack)

    return formatted_data


def filter_by_route_type(json_data, type):
    if json_data == None:
        return None

    filtered_json_data = []
    for data_pack in json_data:
        if data_pack['route_type'] == type:
            if data_pack['route_id'] is not None:
                filtered_json_data.append(data_pack)

    return filtered_json_data


def request_trip_info(api_key):
    url = "https://api.tranzy.dev/v1/opendata/trips"
    headers = {
        "X-Agency-Id": "4",
        "Accept": "application/json",
        "X-API-KEY": api_key
    }

    response = requests.get(url, headers=headers)
    return json.loads(response.text)


def format_trip_data(json_data):
    keys_to_keep = ['route_id', 'trip_id', 'trip_headsign', 'direction_id']
    formatted_data = [{key: data[key] for key in keys_to_keep if key in data} for data in json_data]

    return formatted_data


def request_stop_info(api_key):
    url = "https://api.tranzy.dev/v1/opendata/stops"
    headers = {
        "X-Agency-Id": "4",
        "Accept": "application/json",
        "X-API-KEY": api_key
    }

    response = requests.get(url, headers=headers)
    return json.loads(response.text)


def format_stop_data(json_data):
    keys_to_keep = ['stop_id', 'stop_name', 'stop_lat', 'stop_lon']
    formatted_data = [{key: data[key] for key in keys_to_keep if key in data} for data in json_data]
    return formatted_data


def request_stop_times(api_key):
    url = "https://api.tranzy.dev/v1/opendata/stop_times"
    headers = {
        "X-Agency-Id": "4",
        "Accept": "application/json",
        "X-API-KEY": api_key
    }

    response = requests.get(url, headers=headers)
    return json.loads(response.text)  # Parse the response as JSON


def __execute_query(query, db_cursor, db_connection):
    try:
        db_cursor.execute(query.replace('None', 'NULL'))
        db_connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        # print(query)
        print(f"Failed SQL statement: {cursor.statement}\n")


# *---DATABASE-IMPORT------------------------------------
def insert_in_db(json_data, table_name, update_rows):
    for data in json_data:
        __execute_query(f"INSERT INTO {table_name} ({update_rows}) VALUES {tuple(data.values())}", cursor, connection)


def drop_all_data():
    cursor.execute("DELETE FROM stop_times")
    connection.commit()

    cursor.execute("DELETE FROM stops")
    connection.commit()

    cursor.execute("DELETE FROM routes")
    connection.commit()

    cursor.execute("DELETE FROM trips")
    connection.commit()


    cursor.execute("DELETE FROM public_vehicle")
    connection.commit()


# ?---SETUP-STAGE----------------------------------------
# connect to db
connection = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    database='test1',
    port=3306
)
cursor = connection.cursor()

drop_all_data()

# routes
routes_response = request_routes_info(routes_key)
formatted_routes = format_routes_data(routes_response)
insert_in_db(formatted_routes, "routes", "route_id, route_number, route_full_name, route_type")

# trips
trip_response = request_trip_info(trips_key)
formatted_trip_data = format_trip_data(trip_response)
insert_in_db(formatted_trip_data, "trips", "route_id, trip_id, trip_headsign, direction_type")

# vehicles
response = request_vehicle_info(vehicles_key)
vehicles_response = format_vehicle_data(response)
insert_in_db(vehicles_response, "public_vehicle",
             "vehicle_id, vehicle_type, route_id, trip_id, geo_lat, geo_lon, speed, wheelchair_access")

# stops
stop_response = request_stop_info(stops_key)
formatted_stop_response = format_stop_data(stop_response)
insert_in_db(formatted_stop_response, "stops", "stop_id, stop_name, geo_lat, geo_lon")

# stop times
stop_times_response = request_stop_times(stop_times_key)
insert_in_db(stop_times_response, "stop_times", "trip_id, stop_id, stop_sequence")


# ?----UPDATE-STAGE-------------------------------------------------
def update_table(table_name, table_columns, json_keys, link_at, json_data):
    for data in json_data:
        query = f"UPDATE {table_name}\n SET "
        for index, j_key in enumerate(json_keys):
            # print(f'{table_columns[index]}={data[j_key]}')

            if isinstance(data[j_key], str):
                query += f'{table_columns[index]}="{data[j_key]}", '
            else:
                query += f'{table_columns[index]}={data[j_key]}, '

        query = query[:-2]
        if isinstance(data[link_at[1]], str):
            query += f' WHERE {link_at[0]}="{data[link_at[1]]}"'
        else:
            query += f' WHERE {link_at[0]}={data[link_at[1]]}'

        __execute_query(query, cursor, connection)


maxUpdates = 50
updates = 0
while updates < maxUpdates:
    # update trip info
    updated_trips_response = format_trip_data(request_trip_info(trips_key))
    update_table(
        "trips",
        ["trip_headsign", "direction_type"],
        ["trip_headsign", "direction_id"],
        ["trip_id", "trip_id"],
        updated_trips_response
    )
    print("updt")

    # update vehicle info
    updated_vehicle_response = format_vehicle_data(request_vehicle_info(vehicles_key))
    update_table(
        "public_vehicle",
        ["trip_id", "geo_lat", "geo_lon", "speed"],
        ["trip_id", "latitude", "longitude", "speed"],
        ["vehicle_id", "id"],
        updated_vehicle_response
    )

    updates += 1
    print(f'updated({updates}/{maxUpdates})')
    time.sleep(10)
# ?------------------------------------------------------

cursor.close()
connection.close()





