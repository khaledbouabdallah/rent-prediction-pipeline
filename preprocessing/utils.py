import psycopg2
from psycopg2 import Error
import csv

def create_table_ads_clean():
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
        # Create a table
        create_table_query = '''CREATE TABLE IF NOT EXISTS ads_clean
              (id INTEGER PRIMARY KEY,
              department_name TEXT NOT NULL,
              department_number INT NOT NULL,
              city_name TEXT NOT NULL,
              ad_type INT NOT NULL,
              latitude FLOAT NOT NULL,
              longitude FLOAT NOT NULL,
              price FLOAT NOT NULL,
              area FLOAT NOT NULL,
              energy_DPE INT NOT NULL,
              energy_GES INT NOT NULL,
              furnished INT NOT NULL,
              empty INT NOT NULL,
              bothXX INT NOT NULL,
              Balcon_ou_terrasse INT NOT NULL,
              Garage INT NOT NULL,
              Baignoire INT NOT NULL,
              Jardin INT NOT NULL,
              Grand_sejour INT NOT NULL,
              Stationnement_possible INT NOT NULL,
              Toilettes_privatives INT NOT NULL,
              Salle_de_bains_privative INT NOT NULL,
              Internet_inclus INT NOT NULL,
              Plusieurs_salles_de_bains INT NOT NULL,
              Proximite_transport INT NOT NULL,
              Proximite_commerces INT NOT NULL,
              Sans_vis_a_vis INT NOT NULL,
              Plain_pied INT NOT NULL,
              Ascenseur INT NOT NULL,
              Toilettes_independantes INT NOT NULL,
              Cuisine_equipee INT NOT NULL,
              Cuisine_possible INT NOT NULL,
              Cuisine_indépendante INT NOT NULL,
              Dernier_etage INT NOT NULL,
              Cave_ou_local INT NOT NULL
              )'''
        cursor.execute(create_table_query)
        connection.commit()
    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

def select_all_ads(save=False):
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
        # Select all rows from the table
        cursor.execute("SELECT * FROM ads_clean")
        rows = cursor.fetchall()
        
        if save:
            with open('ads_clean_db.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(rows)
        return rows
    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")            
            
def insert_ad(ad):
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
        # Insert a row into the table
        insert_query = '''INSERT INTO ads_clean (id,department_name, department_number, city_name, ad_type, latitude, longitude, price, area, energy_DPE, energy_GES, furnished, empty, bothXX, Balcon_ou_terrasse, Garage, Baignoire, Jardin, Grand_sejour, Stationnement_possible, Toilettes_privatives, Salle_de_bains_privative, Internet_inclus, Plusieurs_salles_de_bains, Proximite_transport, Proximite_commerces, Sans_vis_a_vis, Plain_pied, Ascenseur, Toilettes_independantes, Cuisine_equipee, Cuisine_possible, Cuisine_indépendante, Dernier_etage, Cave_ou_local)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        
        cursor.execute(insert_query, (ad['id'], ad['department_name'], ad['department_number'], ad['city_name'], ad['ad_type'],
                                      ad['latitude'], ad['longitude'], ad['price'], ad['area'], ad['energy_DPE'], ad['energy_GES'], 
                                      ad['furnished'], ad['empty'], ad['both'], ad['Balcon ou terrasse'], ad['Garage'], ad['Baignoire'], ad['Jardin'], ad['Grand séjour'],
                                      ad['Stationnement possible'], ad['Toilettes privatives'], ad['Salle de bains privative'], ad['Internet inclus'], ad['Plusieurs salles de bains'],
                                      ad['Proximité transport'], ad['Proximité commerces'], ad['Sans vis à vis'], ad['Plain pied'], ad['Ascenseur'], ad['Toilettes indépendantes'],
                                      ad['Cuisine équipée'], ad['Cuisine possible'], ad['Cuisine indépendante'], ad['Dernier étage'], ad['Cave ou local']))
        
        connection.commit()
    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")