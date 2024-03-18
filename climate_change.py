import streamlit as st
import plotly.express as px
import pandas as pd
import json
from streamlit_lottie import st_lottie
import requests



def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


lottie_temperature_meter = load_lottie_url("https://lottie.host/c2f23b2b-cc34-485a-b466-d0c0af815828/zPAxPvR17j.json")
lottie_earth = load_lottie_url("https://lottie.host/7332295c-98ac-4ba6-8ced-51cbf1ebd984/wUgtDvjY8F.json")



df = pd.read_csv(r"climate_change_indicators.csv")
f = open(r'countries.geo.json')
world_json = json.load(f)

year_list = []
for i in range(1963, 2023):
    year = f"F{i}"
    year_list.append(year)

df_melt = pd.melt(df, id_vars=["Country"], value_vars=year_list)
df_melt.rename(columns={"variable": "Year", "value": "Tempurate_Change"}, inplace=True)
df_melt['Year'] = df_melt['Year'].str.replace(r'F', '', regex=True)
df_melt['Year'] = df_melt['Year'].astype(int)
df_melt['Tempurate_Change'] = pd.to_numeric(df_melt['Tempurate_Change'], errors='coerce')

# Find max and min temperature changes
max_tempurate = df_melt.loc[df_melt['Tempurate_Change'].idxmax()]
min_tempurate = df_melt.loc[df_melt['Tempurate_Change'].idxmin()]


# Mean Temperature Change for each Year
mean_tempurate_change_by_year = df_melt.groupby("Year").agg({"Tempurate_Change":"mean"}).reset_index()

# The country with the maximum temperature change for each year
top_countries_year = df_melt.groupby(["Year", "Country"])["Tempurate_Change"].mean().reset_index()
top_countries_year = top_countries_year.groupby("Year").apply(lambda x: x.nlargest(1, "Tempurate_Change")).reset_index(drop=True)

# Streamlit app
st.set_page_config(
    page_title="Climate Change",
    page_icon=":bar_chart:",
    layout="wide"
)


# Title
colT1,colT2 = st.columns([1,2])
with colT2:
    st.title("Change Temperature Dashboard")

#Gif

colG1, colG2, colG3, colG4= st.columns(4)


with colG1:
    st.write("")

with colG2:
    st_lottie(lottie_earth, width=200, height=150)

with colG3:
    st.write("")

with colG4:
    frame_width = 200
    frame_height = 150
    frame_style = f"margin-left: 1000px;"
    st.markdown(
        f"<div style='{frame_style}'>{st_lottie(lottie_temperature_meter, width=frame_width, height=frame_height)}</div>",
        unsafe_allow_html=True
    )







# Selector
st.markdown("<h3 style='text-align: center;'>Select Year</h3>", unsafe_allow_html=True)
selected_year = st.slider("", min_value=int(df_melt['Year'].min()), max_value=int(df_melt['Year'].max()), value=int(df_melt['Year'].min()))

# Filtered data
filtered_df = df_melt[df_melt["Year"] == selected_year]


# Indicators
left_indicator, right_indicator = st.columns(2)
with left_indicator:
    st.subheader(f"**Maximum Tempurate Change ({max_tempurate['Country']} - {max_tempurate['Year']})**")
    st.subheader(f"{max_tempurate['Tempurate_Change']:.2f}°C")

with right_indicator:
    st.subheader(f"**Minumum Tempurate Change ({min_tempurate['Country']} - {min_tempurate['Year']})**")
    st.subheader(f"{min_tempurate['Tempurate_Change']:.2f}°C")

st.markdown("""---""")

# Map
fig_map = px.choropleth(
    filtered_df,
    geojson=world_json,
    featureidkey='properties.name',
    locations='Country',
    color='Tempurate_Change',
    color_continuous_scale='orrd',
    projection='orthographic',
    labels={'Tempurate_Change': 'Tempurate Change (°C)'}
)
fig_map.update_geos(
    fitbounds="locations",
    visible=True
)
fig_map.update_layout(
    geo=dict(
        bgcolor='rgba(0,0,0,0)',
        showland=True,
        showcountries=True
    ),
    margin=dict(l=0, r=0, t=0, b=0),
)

map_col = st.columns(1)[0]

with map_col:
    map_col.plotly_chart(fig_map, use_container_width=True)



#Graphs

fig_line = px.line(mean_tempurate_change_by_year.sort_values("Year", ascending=False), x='Year', y='Tempurate_Change',
              title='Mean Tempurate Change For Each Year', markers=True,
              labels={'Tempurate_Change': 'Tempurate Change (°C)'}, color_discrete_sequence=['#fdbb84'])

fig_line.update_layout(
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=False),
    plot_bgcolor='rgba(0,0,0,0)'
)



fig_bar = px.bar(filtered_df.sort_values("Tempurate_Change", ascending = False).head(10), x='Country',
                 y='Tempurate_Change', color='Tempurate_Change', color_continuous_scale = 'orrd',
                 title='Countries With The Highest Temperature Increase (Top 10)', text="Country",
                 labels={'Tempurate_Change': 'Tempurate Change (°C)'})

fig_bar.update_layout(
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=False),
    plot_bgcolor='rgba(0,0,0,0)'
)




left_graph, right_graph = st.columns(2)

with left_graph:
    left_graph.plotly_chart(fig_line, use_container_width=True)

with right_graph:
    right_graph.plotly_chart(fig_bar, use_container_width=True)


