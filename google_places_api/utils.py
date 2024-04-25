# calculate the distance between two points
from math import sin, cos, sqrt, atan2, radians
import psycopg2
from psycopg2 import Error
import csv

def distance(lat1, lon1, lat2, lon2):
    # lat1, lon1, lat2, lon2 are in degrees
    # return the distance in km
       
    # approximate radius of earth in km
    R = 6373.0
    # convert degrees to radians
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    # change in coordinates
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    # Haversine formula
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    # c is the great circle distance in radians
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance


def create_places_table():
    try:
        # Connect to your PostgreSQL database by providing connection parameters
        connection = psycopg2.connect(
            user="admin",
            password="your_password",
            host="localhost",
            port="5432",
            database="bigdata"
        )

        # Create a cursor object using the connection
        cursor = connection.cursor()
        
        # Drop the table if it exists
        drop_table_query = """DROP TABLE IF EXISTS places"""
        cursor.execute(drop_table_query)
        
    
        # Create a table if it does not exist
        create_table_query = """CREATE TABLE IF NOT EXISTS places(
              id serial PRIMARY KEY,
              id_ad INTEGER, 
              name TEXT NOT NULL,
              primaryType TEXT NOT NULL,
              types TEXT NOT NULL,
              latitude FLOAT NOT NULL,
              longitude FLOAT NOT NULL,
              distance FLOAT NOT NULL
              )"""
              
        cursor.execute(create_table_query)

        connection.commit()
        
    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
            
            
def insert_place(place):
    try:
        # Connect to your PostgreSQL database by providing connection parameters
        connection = psycopg2.connect(
            user="admin",
            password="your_password",
            host="localhost",
            port="5432",
            database="bigdata"
        )

        # Create a cursor object using the connection
        cursor = connection.cursor()
        
        # Insert a row into the places table
        insert_query = '''INSERT INTO places (id_ad, name, primaryType, types, latitude, longitude, distance)
              VALUES (%s, %s, %s, %s, %s, %s, %s); '''
              
        cursor.execute(insert_query, (place['id'], place['name'], place['primaryType'], place['types'], place['latitude'], place['longitude'], place['distance']))

        connection.commit()
        
    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            #print("PostgreSQL connection is closed")
            

def select_all_places(save=False):
    try:
        # Connect to your PostgreSQL database by providing connection parameters
        connection = psycopg2.connect(
            user="admin",
            password="your_password",
            host="localhost",
            port="5432",
            database="bigdata"
        )

        # Create a cursor object using the connection
        cursor = connection.cursor()
        
        # Select all rows from the places table
        select_query = '''SELECT * FROM places; '''
              
        cursor.execute(select_query)

        places = cursor.fetchall()
        if save:
            with open('places.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(("id","ad_id","name","type","types","latitude","longitude","distance"))
                writer.writerows(places)
        
        return places
        
    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")