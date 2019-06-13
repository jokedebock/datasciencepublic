import pandas as pd
import numpy as np
import pgeocode
from pypostalcode import PostalCodeDatabase
import folium # map rendering library
from geopy.geocoders import Nominatim # convert an address into latitude and longitude values
import requests # library to handle requests
from pandas.io.json import json_normalize # tranform JSON file into a pandas dataframe
from sklearn.cluster import KMeans # import k-means from clustering stage
import matplotlib.cm as cm # Matplotlib and associated plotting modules
import matplotlib.colors as colors
import os
import webbrowser


# EXERCISE PART 1: Creating the dataframe and transforming the data
# -----------------------------------------------------------------

d = pd.read_html("http://www.geonames.org/postalcode-search.html?q=&country=BE")
df = d[2]
df.columns = ['SequenceNr', 'City', 'PostalCode','Country', 'Region', 'Province', 'MajorCity']

# Drop rows where Borough is "Not assgined"
df = df.replace('Not assigned', np.nan)
df = df.dropna(subset=['SequenceNr'])
df = df.drop(columns='SequenceNr')
df = df.drop(columns='Country')
df = df.drop(columns= 'Region')

df_antwerp = df[df.MajorCity == "Antwerpen"]

# EXERCISE PART 2: Adding latitude & longitude to the dataframe
# -------------------------------------------------------------

nomi = pgeocode.Nominatim('be')

# Function to search for latitude based on postal code
def searchlatitude(x):
     try:
         t_postalcodeinfo = nomi.query_postal_code(x)
         latitude = t_postalcodeinfo[-3]
         return latitude
     except:
         return "Not found"

# Function to search for longitude based on postal code
def searchlongitude(x):
    try:
        t_postalcodeinfo = nomi.query_postal_code(x)
        longitude = t_postalcodeinfo[-2]
        return longitude
    except:
        return "Not found"


# Add columns Latitude and Longitude
df_antwerp['Latitude'] = df_antwerp.apply(lambda row: searchlatitude(row.PostalCode), axis = 1)
df_antwerp['Longitude'] = df_antwerp.apply(lambda row: searchlongitude(row.PostalCode), axis = 1)
print(df_antwerp)

#
# # Drop the rows for which the postal code was not found
# df = df.replace('Not found', np.nan)
# df = df.dropna(subset=['Latitude'])
#
# print("EXERCISE PART 2:")
# print(df.head())
# print(df.shape)
# print(" ")
#
# # EXERCISE PART 3: Exploring & clustering the neighborhoods of Toronto
# # --------------------------------------------------------------------
#
# print("EXERCISE PART 3:")
# # Create a boolean mask to filter rows where Borough contains "Toronto" and create new dataframe based on mask
# boroughtoronto = df['Borough'].str.contains("Toronto")
# neighborhoods = df[boroughtoronto]
#
# # Get location of Toronto
# address = 'Toronto'
# geolocator = Nominatim(user_agent="toronto_explorer")
# location = geolocator.geocode(address)
# latitude = location.latitude
# longitude = location.longitude
# #print('The geograpical coordinate of Toronto are {}, {}.'.format(latitude, longitude))
#
# # Create map of New York using latitude and longitude values
# map_toronto = folium.Map(location=[latitude, longitude], zoom_start=10)
#
# # Add markers to map
# for lat, lng, borough, neighborhood in zip(neighborhoods['Latitude'], neighborhoods['Longitude'],
#                                            neighborhoods['Borough'], neighborhoods['Neighborhood']):
#     label = '{}, {}'.format(neighborhood, borough)
#     label = folium.Popup(label, parse_html=True)
#     folium.CircleMarker(
#         [lat, lng],
#         radius=5,
#         popup=label,
#         color='blue',
#         fill=True,
#         fill_color='#3186cc',
#         fill_opacity=0.7,
#         parse_html=False).add_to(map_toronto)
#
# # Show map (in Jupyter Notebook)
# map_toronto
#
# # Foursquare credentials
# CLIENT_ID = 'JZNEUC4UMXDUSRH140GO1MW1BXMSJXC14DLPZYWVDR5UJ5P1' # Foursquare ID
# CLIENT_SECRET = 'QDNPZM1Q0KPYYQTP21HWJSHXPRGOG4412PDTDYFYXNEJ3BTR' # Foursquare Secret
# VERSION = '20180605' # Foursquare API version
#
# # Get latitude and longitude for first neighborhood
# neighborhood_latitude = neighborhoods['Latitude'].iloc[0]
# neighborhood_longitude = neighborhoods['Longitude'].iloc[0]
# neighborhood_name = neighborhoods['Neighborhood'].iloc[0]
#
# # Call the Foursquare API
# LIMIT = 100 # limit of number of venues returned by Foursquare API
# radius = 500 # define radius
#
# url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
#     CLIENT_ID,
#     CLIENT_SECRET,
#     VERSION,
#     neighborhood_latitude,
#     neighborhood_longitude,
#     radius,
#     LIMIT)
# results = requests.get(url).json()
#
#
# # Function that extracts the category of the venue
# def get_category_type(row):
#     try:
#         categories_list = row['categories']
#     except:
#         categories_list = row['venue.categories']
#
#     if len(categories_list) == 0:
#         return None
#     else:
#         return categories_list[0]['name']
#
#
# # Clean the json and structure it into a pandas dataframe
# venues = results['response']['groups'][0]['items']
# nearby_venues = json_normalize(venues)  # flatten JSON
# filtered_columns = ['venue.name', 'venue.categories', 'venue.location.lat', 'venue.location.lng'] # filter columns
# nearby_venues = nearby_venues.loc[:, filtered_columns]
# nearby_venues['venue.categories'] = nearby_venues.apply(get_category_type, axis=1) # filter the category for each row
# nearby_venues.columns = [col.split(".")[-1] for col in nearby_venues.columns] # clean columns
# #print(nearby_venues.head())
# #print('{} venues were returned by Foursquare.'.format(nearby_venues.shape[0]))
#
# # Function to repeat the same process to all the neighborhoods
# def getNearbyVenues(names, latitudes, longitudes, radius=500):
#     venues_list = []
#     for name, lat, lng in zip(names, latitudes, longitudes):
#         # create the API request URL
#         url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
#             CLIENT_ID,
#             CLIENT_SECRET,
#             VERSION,
#             lat,
#             lng,
#             radius,
#             LIMIT)
#
#         # make the GET request
#         results = requests.get(url).json()["response"]['groups'][0]['items']
#
#         # return only relevant information for each nearby venue
#         venues_list.append([(
#             name,
#             lat,
#             lng,
#             v['venue']['name'],
#             v['venue']['location']['lat'],
#             v['venue']['location']['lng'],
#             v['venue']['categories'][0]['name']) for v in results])
#
#     nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
#     nearby_venues.columns = ['Neighborhood',
#                              'Neighborhood Latitude',
#                              'Neighborhood Longitude',
#                              'Venue',
#                              'Venue Latitude',
#                              'Venue Longitude',
#                              'Venue Category']
#
#     return (nearby_venues)
#
# # Apply the function to the neighborhoods of Toronto
# toronto_venues = getNearbyVenues(names=neighborhoods['Neighborhood'],
#                                    latitudes=neighborhoods['Latitude'],
#                                    longitudes=neighborhoods['Longitude']
#                                   )
#
# # One hot encoding
# toronto_onehot = pd.get_dummies(toronto_venues[['Venue Category']], prefix="", prefix_sep="")
# toronto_onehot['Neighborhood'] = toronto_venues['Neighborhood'] # Add neighborhood column back to dataframe
# fixed_columns = [toronto_onehot.columns[-1]] + list(toronto_onehot.columns[:-1]) # move neighborhood column to the first column
# toronto_onehot = toronto_onehot[fixed_columns]
#
# # Group by Neighborhood
# toronto_grouped = toronto_onehot.groupby('Neighborhood').mean().reset_index()
#
# # Function to sort venues in descending order
# def return_most_common_venues(row, num_top_venues):
#     row_categories = row.iloc[1:]
#     row_categories_sorted = row_categories.sort_values(ascending=False)
#
#     return row_categories_sorted.index.values[0:num_top_venues]
#
# # Create new dataframe and display the top 10 venues for each neighborhood
# num_top_venues = 10
# indicators = ['st', 'nd', 'rd']
# columns = ['Neighborhood'] # Create columns according to number of top venues
# for ind in np.arange(num_top_venues):
#     try:
#         columns.append('{}{} Most Common Venue'.format(ind+1, indicators[ind]))
#     except:
#         columns.append('{}th Most Common Venue'.format(ind+1))
# neighborhoods_venues_sorted = pd.DataFrame(columns=columns) # Create a new dataframe
# neighborhoods_venues_sorted['Neighborhood'] = toronto_grouped['Neighborhood']
# for ind in np.arange(toronto_grouped.shape[0]):
#     neighborhoods_venues_sorted.iloc[ind, 1:] = return_most_common_venues(toronto_grouped.iloc[ind, :], num_top_venues)
#
# # k-means cluster
# kclusters = 5 # set number of clusters
# toronto_grouped_clustering = toronto_grouped.drop('Neighborhood', 1)
# kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(toronto_grouped_clustering) # run k-means clustering
# kmeans.labels_[0:10]  # Check cluster labels generated for each row in the dataframe
#
# # Create a new dataframe that includes the cluster as well as the top 10 venues for each neighborhood
# neighborhoods_venues_sorted.insert(0, 'Cluster Labels', kmeans.labels_) # Add clustering labels
# toronto_merged = neighborhoods
#
# # Merge toronto_grouped with toronto_data to add latitude/longitude for each neighborhood
# toronto_merged = toronto_merged.join(neighborhoods_venues_sorted.set_index('Neighborhood'), on='Neighborhood')
# toronto_merged.head()
#
# # Visualise the resulting clusters
# map_clusters = folium.Map(location=[latitude, longitude], zoom_start=11) # create map
# x = np.arange(kclusters) # set color scheme for the clusters
# ys = [i + x + (i * x) ** 2 for i in range(kclusters)]
# colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
# rainbow = [colors.rgb2hex(i) for i in colors_array]
# markers_colors = [] # add markers to the map
# for lat, lon, poi, cluster in zip(toronto_merged['Latitude'], toronto_merged['Longitude'],
#                                   toronto_merged['Neighborhood'], toronto_merged['Cluster Labels']):
#     label = folium.Popup(str(poi) + ' Cluster ' + str(cluster), parse_html=True)
#     folium.CircleMarker(
#         [lat, lon],
#         radius=5,
#         popup=label,
#         color=rainbow[cluster - 1],
#         fill=True,
#         fill_color=rainbow[cluster - 1],
#         fill_opacity=0.7).add_to(map_clusters)
#
# map_clusters
#
# filepath = r'''C:\Users\rc01828\PycharmProjects\map.html'''
# map_clusters.save(filepath)
# webbrowser.open('file://' + filepath)
# iframe = map_clusters._repr_html_()