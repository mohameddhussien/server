import sqlite3
import argon2
import cx_Oracle as orcl
from operator import itemgetter
import numpy as np
import uuid

# Set your Oracle connection details
oracle_connection_string = "scott/tiger@localhost:1521/orcl.168.56.1"

lib_dir = "D:\Software\instantclient_21_12"

try:
    orcl.init_oracle_client(lib_dir=lib_dir)
except Exception as err:
    print("Error connecting: cx_Oracle.init_oracle_client()")
    print(err)
# Establish a connection
connection = orcl.connect(oracle_connection_string)


def generate_random_id():
    random_id = str(uuid.uuid4())
    return random_id


def getColumnsNamesFromTable(table_name):
    table_name = table_name.upper()
    cursor = connection.cursor()
    query = "SELECT column_name FROM user_tab_columns WHERE table_name = :table_name"
    cursor.execute(query, {"table_name": table_name})
    columns = cursor.fetchall()
    columns = [column[0] for column in columns]
    return columns


def getEvent(event_key):
    cursor = connection.cursor()
    query = """
            SELECT *
            FROM loe_events e
            JOIN event_details ON e.event_key = event_details.event_key
            WHERE e.event_key = :event_key
            """
    cursor.execute(query, {"event_key": event_key})
    query_result = cursor.fetchone()
    columns = np.concatenate(
        (
            np.array(getColumnsNamesFromTable("loe_events")),
            np.array(getColumnsNamesFromTable("event_details")),
        )
    ).tolist()
    data = dict(zip(columns, query_result))
    query = """SELECT image_url FROM EVENT_IMAGES WHERE event_key = :event_key"""
    cursor.execute(query, {"event_key": event_key})
    images = cursor.fetchall()
    image_urls = list(map(itemgetter(0), images))
    data["IMAGES"] = image_urls
    cursor.close()
    print(data)
    return data


def getAllEvents():
    cursor = connection.cursor()
    query = """SELECT * FROM LOE_EVENTS E
    JOIN EVENT_DETAILS D ON E.EVENT_ID = D.EVENT_ID"""
    cursor.execute(query)
    q_results = cursor.fetchall()
    cursor.close()
    columns = np.concatenate(
        (
            np.array(getColumnsNamesFromTable("loe_events")),
            np.array(getColumnsNamesFromTable("event_details")),
        )
    ).tolist()
    formatted_results = [dict(zip(columns, row)) for row in q_results]
    formatted_results = getImages(q_results, formatted_results)
    return formatted_results


def getImages(events, formatted_data):
    cursor = connection.cursor()
    for i in range(len(events)):
        row = events[i]
        query = """SELECT image_url FROM EVENT_IMAGES WHERE event_id = :event_id"""
        cursor.execute(query, {"event_id": row[0]})
        images = cursor.fetchall()
        image_urls = list(map(itemgetter(0), images))
        formatted_data[i]["IMAGES"] = image_urls
    cursor.close()
    return formatted_data


def CreateUserTable():
    conn = sqlite3.connect("ladiesonlyevents.db")
    cursor = conn.cursor()
    query = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL
    );
    """
    cursor.execute(query)
    conn.commit()
    conn.close()


def CreateOrganizersTable():
    conn = sqlite3.connect("ladiesonlyevents.db")
    cursor = conn.cursor()
    query = """
    CREATE TABLE IF NOT EXISTS organizers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        event_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (event_id) REFERENCES events(id)
    );
    """
    cursor.execute(query)
    conn.commit()
    conn.close()


def GetAllUsers():
    conn = sqlite3.connect("ladiesonlyevents.db")
    cursor = conn.cursor()
    query = "SELECT * FROM users"
    return cursor.execute(query).fetchall()


def InsertUser(data):
    cursor = connection.cursor()
    # Add GENERATED ID.
    data = (generate_random_id(),) + data
    # # HASH user password.
    # data_list = list(data)
    # data_list[5] = hash_password(data_list[5])
    # data = tuple(data_list)
    print(data)
    try:
        cursor.callproc("INSERT_USER_PROC", data)
        connection.commit()
    except Exception as e:
        print(f"Error inserting user: {e}")
        connection.rollback()
        cursor.close()
        return {"error": "email or password is already taken."}
    cursor.close()
    return {"success": "Data Insertion success"}


def hash_password(password):
    # Hash the password using Argon2
    return argon2.PasswordHasher().hash(password)


def GetUser(username, password):
    cursor = connection.cursor()
    query = """SELECT * FROM personal_info WHERE DISPLAY_NAME = :username AND PASS_HASH = :password"""
    user = cursor.execute(
        query, {"username": username, "password": password}
    ).fetchone()
    cursor.close()
    if user:
        return user
    else:
        return {"error": "User not found!"}
