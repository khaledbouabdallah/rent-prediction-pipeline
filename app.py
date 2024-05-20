# ****************************************************
# This is a simple Streamlit app.
# ****************************************************
# run this app with `streamlit run app.py` and
# visit http://localhost:8501
# in your web browser.

import streamlit as st
import streamlit.components.v1 as components
import os
import joblib
import pandas as pd
import numpy as np
from xgboost import XGBRegressor
import shap
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium

import google_places_api.placesApi as placesApi
from google_places_api.utils import distance
from featureEngineering.utils import linear_distance_weighting

API_KEY = os.environ.get("GOOGLE_API_KEY")

@st.cache_data
def call_api(input):
    radius = 2000.0  # meters, max=50000 (50km)
    # Request parameters
    maxResults = 20 # max=20
    rankBy = "POPULARITY" # "POPULARITY" or "DISTANCE"
    #rankPreference": ""
    includedTypes = ["train_station","subway_station","bus_station","bus_stop" ] #"hospital","shopping_mall", "school"
    fieldMask = ["places.primaryType",
                 "places.displayName",
                 'places.types',
                 "places.location"]
    includedPrimaryTypes = None
    api = placesApi.PlacesApi(API_KEY)
    response = api.searchNearby(latitude=input['latitude'], longitude=input['longitude'], radius=radius,
                        fieldMask= fieldMask, includedTypes= includedTypes,
                        includedPrimaryTypes = includedPrimaryTypes, maxResults=20, rankPreference=rankBy)
    return response

@st.cache_data
def load_data():
    explainer = joblib.load(open('prediction/models/xgboost_explainer.pkl', 'rb'))
    data = pd.read_csv('data/ads_stations_weighted.csv')
    model = joblib.load(open('prediction/models/xgboost_model.pkl', 'rb'))
    scaler = joblib.load(open('prediction/models/xgboost_scaler.pkl', 'rb'))
    explanation = joblib.load(open('prediction/models/xgboost_explanation.pkl', 'rb'))
    return data, model, explainer, scaler, explanation

def st_shap(plot, height=None):
    shap_html = f"<head>{shap.getjs()}</head><body>{plot.html()}</body>"
    components.html(shap_html, height=height)    

def reorder_dict(d, order):
    return {k: d[k] for k in order}

def clean_energy(x):
    if x == 'A':
        return 1
    elif x == 'B':
        return 2
    elif x == 'C':
        return 3
    elif x == 'D':
        return 4
    elif x == 'E':
        return 5
    elif x == 'F':
        return 6
    elif x == 'G':
        return 7
    else:
        return 4

def oridinal_ad_type(x):
    if x == 'Chambre':
        return 0
    elif x == 'Studio':
        return 1
    elif x == 'Appartement':
        return 2
    elif x == 'Maison':
        return 3
    
def furnished(x):
    if x == 'furnished':
        return (1,0,0)
    elif x == 'empty':
        return (0,1,0)
    elif x == 'both':
        return (0,0,1)

def main():
    
    input = {}
    data, model, explainer, scaler, explanation = load_data()
    # shap_values = explanation.values
    # X = data.drop(columns=['price'])
    # y = data['price']
    #X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0, random_state=42)
    #X_train = scaler.transform(X_train)
    #X_train = pd.DataFrame(X_train, columns=X.columns)
    
    st.title('Renting Price Prediction App 🏠')
    st.write('This is a simple Streamlit app to test renting prediction model which was created for the "Big Data" course at the University of Paris (DCI)')
    st.write('The model uses the XGBoost algorithm to predict the price of an apartment/house based on its features')
    st.write('The model was trained on 7524 real french real estate ads which were scrapped from the internet')
    st.write('The project encompasses the following steps: data collection, data cleaning, feature engineering, model training, and model deployment')
    st.warning('The model is only used for experimental purposes and should not be used for real estate transactions!')
    st.divider()
    st.header('important features of the apartment (required for prediction)')
    
    
    input['area'] = float(st.text_input('Enter the area of the apartment (in square meter):', '25'))
    
    type = st.selectbox('Select the type of the apartment:', ('Chambre', 'Studio', 'Appartement', 'Maison'))
    input['ad_type'] = oridinal_ad_type(type)
    
    st.subheader('Location of the apartment')
    st.write('Enter the longitude and latitude of the apartment')
    st.info('You can find the longitude and latitude of a location using Google Maps!')
    input['latitude'] = float(st.text_input('Enter the latitude of the apartment:', '48.856711643433755'))
    input['longitude'] = float(st.text_input('Enter the longitude of the apartment:', '2.331784493600353'))
    m = folium.Map(location=[input['latitude'], input['longitude']], zoom_start=16)
    folium.Marker(location=[input['latitude'], input['longitude']], popup='Your apartment/house', icon=folium.Icon(color='red')).add_to(m)
    st_data = st_folium(m, width=725)
    

    st.divider()
    st.header('optional features of the apartment')
    st.write('You can skip these features if you do not know them, but they can help improve the prediction!')
    
    st.subheader("Energy consumption of the apartment")
    st.write("Choose the energy consumption of the apartment, if you don't know it leave it as it is!")
    st.image('resources/energy.jpg', use_column_width=True)
    energy_DPE = st.selectbox('Select the energy consumption of the apartment (DPE):', ('A', 'B', 'C', 'D', 'E', 'F', 'G'), index=3)
    energy_GES = st.selectbox('Select the energy consumption of the apartment (GES):', ('A', 'B', 'C', 'D', 'E', 'F', 'G'), index=3)
    input['energy_DPE'] = clean_energy(energy_DPE)
    input['energy_GES'] = clean_energy(energy_GES)
    
    st.subheader("Features of the apartment")
    st.write("Select the features of the apartment, if you don't know them leave them as they are!")
    # furnished', 'empty', 'both', 'Stationnement possible',
    #    'Toilettes indépendantes', 'Salle de bains privative', 'Dernier étage',
    #    'Plain pied', 'Cuisine équipée', 'Sans vis à vis', 'Cave ou local',
    #    'Internet inclus', 'Toilettes privatives', 'Balcon ou terrasse',
    #    'Grand séjour', 'Cuisine possible', 'Garage', 'Baignoire',
    #    'Proximité transport', 'Proximité commerces', 'Jardin',
    #    'Plusieurs salles de bains', 'Cuisine indépendante', 'Ascenseur',
       
    st.write("Is the apartment furnished? (when you rent it)")
    st.info("both = you have the choice to rent it furnished or empty")
    input['furnished'],input['empty'], input['both'] = furnished(st.selectbox('Furnished:', ('furnished', 'empty', 'both'), index=2))
    
    # use two columns
    col1, col2 = st.columns(2)
    with col1:
        input['Stationnement possible'] = int(st.checkbox('Stationnement possible'))
        input['Toilettes indépendantes'] = int(st.checkbox('Toilettes indépendantes'))
        input['Salle de bains privative'] = int(st.checkbox('Salle de bains privative'))
        input['Dernier étage'] = int(st.checkbox('Dernier étage'))
        input['Plain pied'] = int(st.checkbox('Plain pied'))
        input['Cuisine équipée'] = int(st.checkbox('Cuisine équipée'))
        input['Sans vis à vis'] = int(st.checkbox('Sans vis à vis'))
        input['Cave ou local'] = int(st.checkbox('Cave ou local'))
        input['Internet inclus'] = int(st.checkbox('Internet inclus'))
        input['Toilettes privatives'] = int(st.checkbox('Toilettes privatives'))
    
    with col2:
        input['Balcon ou terrasse'] = int(st.checkbox('Balcon ou terrasse'))
        input['Grand séjour'] = int(st.checkbox('Grand séjour'))
        input['Cuisine possible'] = int(st.checkbox('Cuisine possible'))
        input['Garage'] = int(st.checkbox('Garage'))
        input['Baignoire'] = int(st.checkbox('Baignoire'))
        input['Proximité transport'] = int(st.checkbox('Proximité transport'))
        input['Proximité commerces'] = int(st.checkbox('Proximité commerces'))
        input['Jardin'] = int(st.checkbox('Jardin'))
        input['Plusieurs salles de bains'] = int(st.checkbox('Plusieurs salles de bains'))
        input['Cuisine indépendante'] = int(st.checkbox('Cuisine indépendante'))
        input['Ascenseur'] = int(st.checkbox('Ascenseur'))
        
    
        
    st.write('You can now click the button below to get the prediction')
    if st.button('Predict'):
        st.divider()
        st.title('Prediction')
        st.write('User input: ')
        st.write(input)
        # get google places api data for the location
        st.write('Getting data from Google Places API...')
        st.info('Our model uses the distance to the closest stations (bus,train and metro) to improve the prediction!')
        st.image('resources/api.png', width= 1000)
        response = call_api(input)
        st.write('Data received from Google Places API')
        st.write(response)
        st.write('Close stations and bus stops near the apartment: ')
        places = []
        for place in response.json()['places']:
            places.append({
                'primaryType': place['primaryType'],
                'latitude': place['location']['latitude'],
                'longitude': place['location']['longitude'],
                'distance': distance(input['latitude'], input['longitude'], place['location']['latitude'], place['location']['longitude']),
                'name': place['displayName']['text'],
                'types': ';'.join(place['types']),
            })   
            #marker = folium.Marker(location=[place['location']['latitude'], place['location']['longitude']], popup=place['displayName']['text'], icon=folium.Icon(color='blue')).add_to(m)
        dfs = pd.DataFrame(places)
        #_ = st_folium(m, width=725)
        st.write(dfs)
        # show the appartement and the close stations on a map
        st.map(dfs)
        
        # calculate linear distance scores
        primary_types = ['transit_station', 'bus_stop',
                        'train_station', 'bus_station',
                        'subway_station']
        max_distance = 2  # for linear distance weighting
        for type in primary_types:
            distances = []
            for row in dfs[dfs["primaryType"] == type].iterrows():
                distances.append(row[1]["distance"])
            input["linear_score" + "_" + type] = sum(linear_distance_weighting(distances, max_distance))
        st.write('Linear distance scores: ')
        st.metric('Train station', input["linear_score_train_station"])
        st.metric('Subway station', input["linear_score_subway_station"])
        st.metric('Bus station', input["linear_score_bus_station"])
        st.metric('Bus stop', input["linear_score_bus_stop"])
        # load the model
        st.write('Loading the model...')
        
        input = reorder_dict(input, ['ad_type', 'latitude', 'longitude', 'area', 'energy_DPE', 'energy_GES',
       'furnished', 'empty', 'both', 'Stationnement possible',
       'Toilettes indépendantes', 'Salle de bains privative', 'Dernier étage',
       'Plain pied', 'Cuisine équipée', 'Sans vis à vis', 'Cave ou local',
       'Internet inclus', 'Toilettes privatives', 'Balcon ou terrasse',
       'Grand séjour', 'Cuisine possible', 'Garage', 'Baignoire',
       'Proximité transport', 'Proximité commerces', 'Jardin',
       'Plusieurs salles de bains', 'Cuisine indépendante', 'Ascenseur',
       'linear_score_transit_station', 'linear_score_bus_stop',
       'linear_score_train_station', 'linear_score_bus_station',
       'linear_score_subway_station'])
        df = pd.DataFrame([input])
        df = scaler.transform(df)
        df = pd.DataFrame(df, columns=input.keys())
        prediction = model.predict(df)
        st.write('Prediction: ')
        st.metric('Price', round(prediction[0]), '€',)
        
        st.divider()
        st.title('Explanation')
        st.markdown('In this section, we will explain the prediction using __SHAP__ values, which show the contribution of each feature to the prediction by using __game theory__')   
        st.header('Global Explanation')
        st.write('The following plot shows the importance of each feature in the prediction')
        st.write('we can see that the area of the apartment is the most important feature in the prediction')
        st.write('The location of the apartment is also important, especially the distance to the metro station')
        st.write('Other features like the multiple bathrooms and having access to an elevator also have a great impact on the prediction')
        fig = plt.figure()
        shap.plots.beeswarm(explanation)
        st.pyplot(fig)
        st.header('Local Explanation')
        st.write('The following plot shows how the features contribute to the prediction of your apartment/house price!')
        st.info("Tip: You can play with the features to see how they affect the prediction and the plot!")
        shap_values_new_instance = explainer.shap_values(df.iloc[0].to_numpy().reshape(1, -1))
        st_shap(shap.force_plot(explainer.expected_value, shap_values_new_instance, df.iloc[0]))


if __name__ == '__main__':
    main()






