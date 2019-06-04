import pandas as pd
import numpy as np
from pypostalcode import PostalCodeDatabase

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

print(df)

