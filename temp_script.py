import geopandas as gpd
import pandas as pd

# Load GeoJSON from the Amsterdam open data URL
url = 'https://maps.amsterdam.nl/open_geodata/geojson_lnglat.php?KAARTLAAG=INDELING_STADSDEEL&THEMA=gebiedsindeling'

print('Loading GeoJSON from Amsterdam...')
gdf = gpd.read_file(url)

print('\n=== Column Names ===')
print(gdf.columns.tolist())

print('\n=== Data Shape ===')
print(f'Rows: {len(gdf)}, Columns: {len(gdf.columns)}')

print('\n=== First Few Rows ===')
print(gdf.head())

print('\n=== Data Types ===')
print(gdf.dtypes)
