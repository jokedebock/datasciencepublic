import pandas as pd
import numpy as np

d = pd.read_html("https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M")

df = d[0]
df.columns = ['PostalCode', 'Borough', 'Neighborhood']

df = df.replace('Not assigned', np.nan)

df = df.dropna(subset=['Borough'])

df = df.groupby('Borough', as_index=False).agg(lambda x: ', '.join(set(x.dropna())))

def fx(x):
    if (x['Neighborhood']):
        return x['Neighborhood']
    else:
        return x['Borough']

df['Neighborhood'] = df.apply(lambda x : fx(x),axis=1)

print(df.shape)


