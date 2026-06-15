import pandas as pd
import streamlit as st
import geopandas as gpd
from streamlit_folium import st_folium
import folium
import matplotlib.pyplot as plt
import io
import base64

st.set_page_config(
    page_title="HARTstikke gezond - Kaart",
    page_icon="🫀",
    layout="wide",
)

st.title("📍 Kaart van Amsterdam")
st.markdown("Stadsdelen indeling van Amsterdam - Gekleurd op actieve minuten per dag")
st.markdown("*Gebaseerd op Nederlandse gezondheidsnorm: 21-30 minuten per dag*")

# Gezondheidsdata laden en aggregeren
gezondheid_data = pd.read_csv(r'BuurtData\anonieme_buurtbewoners_gezondheid.csv', sep=',')
actieve_minuten_per_buurt = (
    gezondheid_data
    .groupby('Buurt')['Actieve_minuten_per_dag']
    .mean()
    .reset_index()
)
actieve_minuten_per_buurt.columns = ['Buurt', 'Actieve_minuten']
actieve_minuten_per_buurt['Actieve_minuten'] = actieve_minuten_per_buurt['Actieve_minuten'].round(1)

# Aantal deelnemers per buurt
participants = (
    gezondheid_data
    .groupby('Buurt')
    .size()
    .reset_index(name='Aantal_deelnemers')
)
# Voeg deelnemers toe aan de overzichtstabel
actieve_minuten_per_buurt = actieve_minuten_per_buurt.merge(participants, on='Buurt', how='left')

# GeoJSON laden
mapsdata = gpd.read_file(
    'https://maps.amsterdam.nl/open_geodata/geojson_lnglat.php?KAARTLAAG=INDELING_STADSDEEL&THEMA=gebiedsindeling'
)

# Gegevens samenvoegen met kaartdata
# De GeoJSON gebruikt 'Stadsdeel' als naam kolom
mapsdata = mapsdata.merge(
    actieve_minuten_per_buurt,
    left_on='Stadsdeel',
    right_on='Buurt',
    how='left'
)

# Functie voor kleurkoding op basis van gezondheidseis
def get_color(actieve_minuten):
    if pd.isna(actieve_minuten):
        return '#CCCCCC'  # Grijs voor missing data
    elif actieve_minuten < 21:
        return '#FF4444'  # Rood: onder minimum
    elif actieve_minuten <= 30:
        return "#4597CA"  # Geel: binnen norm
    else:
        return "#257A25"  # Groen: boven norm

# Custom kaart maken met folium
m = folium.Map(
    location=[52.3676, 4.9041],
    zoom_start=11,
    tiles='OpenStreetMap'
)

# Voeg elke buurt toe met juiste kleuring
for idx, row in mapsdata.iterrows():
    color = get_color(row['Actieve_minuten'])
    
    # Bereken percentage van doel (30 min) en maak piechart image
    pct = None
    if pd.notna(row['Actieve_minuten']):
        pct = max(0, min(100, (row['Actieve_minuten'] / 30.0) * 100))
    else:
        pct = 0

    # Maak donut chart als PNG in-memory
    fig, ax = plt.subplots(figsize=(1.2, 1.2))
    achieved = pct
    remaining = 100 - achieved
    if achieved <= 0:
        sizes = [1]
        colors = ['#e6e6e6']
    else:
        sizes = [achieved, remaining]
        colors = ['#44BB44', "#f00c0c"]

    wedges, _ = ax.pie(sizes, colors=colors, startangle=90, wedgeprops={'width':0.5, 'edgecolor':'white'})
    ax.set_aspect('equal')
    ax.axis('off')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', transparent=True)
    plt.close(fig)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode('utf-8')

    # Tooltip HTML met afbeelding (zichtbaar bij hover)
    tooltip_html = f"<div style='text-align:left; font-size:12px;'>"
    tooltip_html += f"<b>{row['Stadsdeel']}</b><br>Actieve minuten: {row['Actieve_minuten']} min<br>Aantal deelnemers: {row.get('Aantal_deelnemers', 0)}<br>Doel behaald: {pct:.0f}%<br>"
    tooltip_html += f"<img src=\"data:image/png;base64,{img_b64}\" style=\"width:80px; height:80px; margin-top:6px;\">"
    tooltip_html += "</div>"

    tooltip = folium.Tooltip(tooltip_html, sticky=True)

    folium.GeoJson(
        data=row.geometry.__geo_interface__,
        style_function=lambda x, col=color: {
            'fillColor': col,
            'color': 'white',
            'weight': 2,
            'fillOpacity': 0.7
        },
        popup=f"<b>{row['Stadsdeel']}</b><br>Actieve minuten: {row['Actieve_minuten']} min<br>Aantal deelnemers: {row.get('Aantal_deelnemers', 0)}",
        tooltip=tooltip
    ).add_to(m)

# Voeg legenda toe
legend_html = '''
<div style="position: fixed; 
            bottom: 50px; right: 50px; width: 280px; height: auto; 
            background-color: white; border:2px solid grey; z-index:9999; 
            font-size:14px; padding: 12px; border-radius: 5px;">
    <p style="margin: 0 0 8px 0; font-weight: bold;">Activiteitsnorm Nederland</p>
    <p style="margin: 5px 0; font-size: 12px;">
        <span style="display: inline-block; width: 15px; height: 15px; background-color: #FF4444; margin-right: 8px; border-radius: 2px;"></span>
        &lt; 21 minuten (onder norm)
    </p>
    <p style="margin: 5px 0; font-size: 12px;">
        <span style="display: inline-block; width: 15px; height: 15px; background-color: #4597CA; margin-right: 8px; border-radius: 2px;"></span>
        21-30 minuten (norm bereikt)
    </p>
    <p style="margin: 5px 0; font-size: 12px;">
        <span style="display: inline-block; width: 15px; height: 15px; background-color: #257A25; margin-right: 8px; border-radius: 2px;"></span>
        &gt; 30 minuten (boven norm)
    </p>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Kaart tonen in Streamlit
st_folium(m, width=1200, height=700)

# Link naar informatie
st.markdown("---")
st.markdown("📖 [Lees meer over Nederlandse gezondheidsnormen en actieve beweging]"
"(https://www.kenniscentrumsportenbewegen.nl/beweegrichtlijnen/)")

st.markdown("---")
# Statistieken tonen
st.subheader("📊 Overzicht actieve minuten per wijk")
stats_df = actieve_minuten_per_buurt.sort_values('Actieve_minuten', ascending=False)
st.dataframe(stats_df, use_container_width=True)

st.markdown("---")
if st.button("🔙 Terug naar dashboard"):
    st.switch_page("app.py")
