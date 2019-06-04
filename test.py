import pandas as pd
import numpy as np
from pypostalcode import PostalCodeDatabase
import folium # map rendering library
from geopy.geocoders import Nominatim # convert an address into latitude and longitude values

d = pd.read_html("https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M")

df = d[0]
df.columns = ['PostalCode', 'Borough', 'Neighborhood']

df = df.replace('Not assigned', np.nan)

df = df.dropna(subset=['Borough'])

df = df.groupby('PostalCode', as_index=False).agg(lambda x: ', '.join(set(x.dropna())))

def fx(x):
    if (x['Neighborhood']):
        return x['Neighborhood']
    else:
        return x['Borough']

df['Neighborhood'] = df.apply(lambda x : fx(x),axis=1)

#print(df)


def searchlatitude(x):
    #print(x)
    pcdb = PostalCodeDatabase()
    try:
        location = pcdb[x]
        #print(x, ", ", location.latitude)
        return location.latitude
    except:
        return "Not found"

def searchlongitude(x):
    #print(x)
    pcdb = PostalCodeDatabase()
    try:
        location = pcdb[x]
        return location.longitude
    except:
        return "Not found"

df['Latitude'] = df.apply(lambda row: searchlatitude(row.PostalCode), axis = 1)
df['Longitude'] = df.apply(lambda row: searchlongitude(row.PostalCode), axis = 1)

df = df.replace('Not found', np.nan)

df = df.dropna(subset=['Latitude'])

#print(df['Borough'])

#boolean mask
boroughtoronto = df['Borough'].str.contains("Toronto")
neighborhoods = df[boroughtoronto]
#print(df[boroughtoronto])

address = 'Toronto'
geolocator = Nominatim(user_agent="toronto_explorer")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinate of Toronto are {}, {}.'.format(latitude, longitude))

# create map of New York using latitude and longitude values
map_toronto = folium.Map(location=[latitude, longitude], zoom_start=10)

# add markers to map
for lat, lng, borough, neighborhood in zip(neighborhoods['Latitude'], neighborhoods['Longitude'],
                                           neighborhoods['Borough'], neighborhoods['Neighborhood']):
    label = '{}, {}'.format(neighborhood, borough)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_toronto)

map_toronto
