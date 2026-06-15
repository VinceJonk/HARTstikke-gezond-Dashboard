import geopandas as gpd
import pandas as pd

# Load GeoJSON from the Amsterdam open data URL
url = 'https://maps.amsterdam.nl/open_geodata/geojson_lnglat.php?KAARTLAAG=INDELING_STADSDEEL&THEMA=gebiedsindeling'

gdf = gpd.read_file(url)

print('\n=== All Rows (without geometry column) ===')
print(gdf.drop('geometry', axis=1).to_string())

print('\n=== Summary Statistics ===')
print(gdf[['Oppervlakte_m2']].describe())
