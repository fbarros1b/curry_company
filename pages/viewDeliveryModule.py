import time
import folium as fo
from streamlit_folium import folium_static
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import plotly.express as px
import streamlit as st

begin = time.time()

st.set_page_config(page_title='Visão Entregadores', layout='wide')

# Lendo o arquivo
df = pd.read_csv('pythonFastTrackTrain.csv')
now1 = time.time()
print('Arquivo lido ' + str(round(now1-begin, 3)))

# Fazendo a limpeza e conversão dos dados
# Removendo as linhas que possuem Delivery_person_Age ou multiple_deliveries como NaN
df1 = df.loc[(df['Delivery_person_Age']!='NaN ') & (df['multiple_deliveries']!='NaN '), :]

# Resetando o índice depois das limpezas. Sem isso os números de índice podem pular, 
# causando erro em uma eventual chamada. O drop=True não deixa ele criar uma coluna
# extra de index.
df1 = df1.reset_index(drop=True)

# Convertendo para int
df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

# Convertendo ratings para float
df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

# Convertendo a entrega para data
df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

# Retirando o espaço no final dos valores
df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
now2 = time.time()
print('Limpeza feita ' + str(round(now2-now1, 3)))

# Streamlit
# Barra lateral
# st.dataframe(df1)
st.header('Marketplace Visão Entregadores')
st.sidebar.image(Image.open('pineapple.jpg'), width=120)
st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')

st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')
dateValue = st.sidebar.slider('Até qual valor?',
                               value=pd.datetime(2022, 4, 1),
                               min_value=pd.datetime(2022, 2, 12),
                               max_value=pd.datetime(2022, 4, 6),
                               format='DD/MM/YYYY')
df1 = df1.loc[df1['Order_Date'] < dateValue, :]

st.sidebar.markdown("""---""")

trafficValue = st.sidebar.multiselect('Quais as condições do trânsito?',
                                      ['Low', 'Medium', 'High', 'Jam'],
                                      default=['Low', 'Medium', 'High', 'Jam'])
df1 = df1.loc[df1['Road_traffic_density'].isin(trafficValue), :]

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by FNunes')
now1 = now2
now2 = time.time()
print('Menu lateral montado ' + str(round(now2-now1, 3)))

# Layout principal
# Manteve as tabs só para manter o padrão.
tab1, tab2, tab3 = st.tabs(['Visão Estratégica', '_', '_'])
with tab1:
  with st.container():
    st.markdown('### Overall metrics')
    col1, col2, col3, col4 = st.columns(4, gap='large')
    dfAuxPersonAge = df1.loc[:, 'Delivery_person_Age']
    dfAuxVehicleCondition = df1.loc[:, 'Vehicle_condition']
    with col1:
      #st.header('Maior idade')
      st.metric('Maior idade', dfAuxPersonAge.max())
    with col2:
      #st.header('Menor idade')
      st.metric('Menor idade', dfAuxPersonAge.min())
    with col3:
      st.metric('Melhor condicação', dfAuxVehicleCondition.max())
    with col4:
      st.metric('Pior condicação', dfAuxVehicleCondition.min())
    now1 = now2
    now2 = time.time()
    print('Primeira linha gerada ' + str(round(now2-now1, 3)))

  with st.container():
    st.markdown("""---""")
    st.markdown('### Avaliações')
    col1, col2 = st.columns(2)
    with col1:
      st.markdown('##### Avaliação média por entregador')
      st.dataframe(df1.loc[:, 
                          ['Delivery_person_ID',                                                                                                        'Delivery_person_Ratings']].groupby('Delivery_person_ID').mean().reset_index())
      now1 = now2
      now2 = time.time()
      print('Avaliação média por entregador gerado ' + str(round(now2-now1, 3)))

    with col2:
      st.markdown('##### Avaliação média por trânsito')
      dfTraffic = df1.loc[:, ['Road_traffic_density', 'Delivery_person_Ratings']]
      dfTraffic = dfTraffic.groupby('Road_traffic_density').agg({'Delivery_person_Ratings':['mean', 'std']}).reset_index()
      dfTraffic.columns = ['Traffic', 'Mean', 'Std']
      st.dataframe(dfTraffic)
      now1 = now2
      now2 = time.time()
      print('Avaliação média por trânsito gerado ' + str(round(now2-now1, 3)))

      st.markdown('##### Avaliação média por clima')
      dfWeather = df1.loc[:, ['Weatherconditions', 'Delivery_person_Ratings']]
      dfWeather = dfWeather.groupby('Weatherconditions').agg({'Delivery_person_Ratings':['mean', 'std']}).reset_index()
      dfWeather.columns = ['Weather', 'Mean', 'Std']
      st.dataframe(dfWeather)
      now1 = now2
      now2 = time.time()
      print('Avaliação média por clima gerado ' + str(round(now2-now1, 3)))

  with st.container():
    st.markdown("""---""")
    st.markdown('### Velocidade de Entrega')
    col1, col2 = st.columns(2)
    with col1:
      st.subheader('Entregadores mais rápidos')
      dfCities = df1.loc[df1['City']!='NaN', ['City', 'Time_taken(min)']]
      dfCities.dropna(inplace=True)
      dfCities['Time_taken(min)'] = dfCities['Time_taken(min)'].str[6:].astype(int)
      dfCities = dfCities.groupby(['City']).min().reset_index()
      st.dataframe(dfCities)
      now1 = now2
      now2 = time.time()
      print('Entregadores mais rápidos gerado ' + str(round(now2-now1, 3)))

    with col2:
      st.subheader('Entregadores mais lentos')
      dfCities = df1.loc[df1['City']!='NaN', ['City', 'Time_taken(min)']]
      dfCities.dropna(inplace=True)
      dfCities['Time_taken(min)'] = dfCities['Time_taken(min)'].str[6:].astype(int)
      dfCities = dfCities.groupby(['City']).max().reset_index()
      st.dataframe(dfCities)
      now1 = now2
      now2 = time.time()
      print('Entregadores mais lentos gerado ' + str(round(now2-now1, 3)))

print('Tempo total ' + str(round(now2-begin, 3)))
