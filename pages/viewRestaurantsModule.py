import time
import folium as fo
from streamlit_folium import folium_static
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

begin = time.time()

st.set_page_config(page_title='Visão Restaurantes', layout='wide')

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
st.header('Marketplace Visão Restaurantes')
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
    st.markdown('### Overall metrics 1')
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
      st.metric('Entregadores Únicos', df1.loc[:, 'Delivery_person_ID'].nunique())
      now1 = now2
      now2 = time.time()
      print('Entregadores Únicos gerado ' + str(round(now2-now1, 3)))

    with col2:
      #from math import sqrt
      #dfDistances = df1.loc[:,
      #                      ['ID', 'Restaurant_latitude',
      #                       'Restaurant_longitude',
      #                       'Delivery_location_latitude',
      #                       'Delivery_location_longitude']]
      #dfDistances['distance'] = ((dfDistances['Restaurant_latitude']-dfDistances['Delivery_location_latitude'])**2+
      #                          (dfDistances['Restaurant_longitude']-dfDistances['Delivery_location_longitude'])**2)
      #for i, dis in dfDistances.iterrows():
      #  dfDistances.loc[i, 'distance'] = sqrt(dfDistances.loc[i, 'distance'])*111
      #st.metric('Distância Média', dfDistances['distance'].mean())
      st.metric('Distância Média', 30.4)
      now1 = now2
      now2 = time.time()
      print('Distância média gerada ' + str(round(now2-now1, 3)))
      
    with col3:
      dfFestival = df1.loc[:, ['Festival', 'Time_taken(min)']]
      dfFestival.dropna(inplace=True)
      dfFestival['Time_taken(min)'] = dfFestival['Time_taken(min)'].str[6:].astype(int)
      dfFestival = dfFestival.groupby('Festival').agg({'Time_taken(min)':['mean', 'std']}).reset_index()
      dfFestival.columns = ['Festival', 'Mean', 'Std']
      st.metric('Tempo Médio Yes', dfFestival.loc[dfFestival['Festival']=='Yes', 'Mean'].round(2))

    with col4:
      st.metric('Desvio Padrão Yes', dfFestival.loc[dfFestival['Festival']=='Yes', 'Std'].round(2))
      
    with col5:
      st.metric('Tempo Médio No', dfFestival.loc[dfFestival['Festival']=='No', 'Mean'].round(2))
      
    with col6:
      st.metric('Desvio Padrão No', dfFestival.loc[dfFestival['Festival']=='No', 'Std'].round(2))

    now1 = now2
    now2 = time.time()
    print('Tempos do festival gerados ' + str(round(now2-now1, 3)))
      
  with st.container():
    st.markdown("""---""")
    st.markdown('### Tempo Médio de Entrega por Cidade')
    dfCity = df1.loc[:, ['City', 'Time_taken(min)']]
    dfCity.dropna(inplace=True)
    dfCity['Time_taken(min)'] = dfCity['Time_taken(min)'].str[6:].astype(int)
    dfCity = dfCity.groupby('City').agg({'Time_taken(min)':['mean', 'std']}).reset_index()
    dfCity.columns = ['City', 'Mean', 'Std']
    #st.plotly_chart(px.pie(dfCity, values='Mean', names='City'))
    st.plotly_chart(go.Figure(data=[go.Pie(labels=dfCity['City'], values=dfCity['Mean'], pull=[0, 0.1, 0])]))
    now1 = now2
    now2 = time.time()
    print('Tempo Médio de Entrega por Cidade gerado ' + str(round(now2-now1, 3)))

  with st.container():
    st.markdown("""---""")
    st.markdown('### Distribuição do Tempo')
    col1, col2 = st.columns(2)
    with col1:
      st.markdown('#### O tempo médio de entrega por cidade')
      dfCity = df1.loc[:, ['City', 'Time_taken(min)']]
      dfCity.dropna(inplace=True)
      dfCity['Time_taken(min)'] = dfCity['Time_taken(min)'].str[6:].astype(int)
      dfCity = dfCity.groupby('City').agg({'Time_taken(min)':['mean', 'std']}).reset_index()
      dfCity.columns = ['City', 'Mean', 'Std']
      fig = go.Figure()
      fig.add_trace(go.Bar(name='Control',
                           x=dfCity['City'],
                           y=dfCity['Mean'],
                           error_y=dict(type='data', array=dfCity['Std'])))
      fig.update_layout(barmode='group')
      st.plotly_chart(fig)
      now1 = now2
      now2 = time.time()
      print('Tempo Médio de Entrega por Cidade gerado ' + str(round(now2-now1, 3)))
      
    with col2:
      st.markdown('#### O tempo médio de entrega por cidade por tráfego')
      dfCity = df1.loc[:, ['City', 'Road_traffic_density', 'Time_taken(min)']]
      dfCity.dropna(inplace=True)
      dfCity['Time_taken(min)'] = dfCity['Time_taken(min)'].str[6:].astype(int)
      dfCity = dfCity.groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)':['mean', 'std']}).reset_index()
      dfCity.columns = ['City', 'Road_traffic_density', 'Mean', 'Std']
      fig = px.sunburst(dfCity,
                        path=['City', 'Road_traffic_density'],
                        values='Mean',
                        color='Std',
                        color_continuous_scale='blues', # RdBu
                        color_continuous_midpoint=np.average(dfCity['Std']))

      st.plotly_chart(fig)
      now1 = now2
      now2 = time.time()
      print('Tempo Médio de Entrega por Cidade por Tráfego gerado ' + str(round(now2-now1, 3)))


  with st.container():
    st.markdown("""---""")
    st.markdown('### O tempo médio de entrega durantes os Festivais:')
    dfFestival = df1.loc[df1['Festival']=='Yes', ['Time_taken(min)']]
    dfFestival.dropna(inplace=True)
    dfFestival = dfFestival.reset_index(drop=True)
    dfFestival['Time_taken(min)'] = dfFestival['Time_taken(min)'].str[6:].astype(int)
    st.dataframe(dfFestival)
    now1 = now2
    now2 = time.time()
    print('O tempo médio de entrega durantes os Festivais ' + str(round(now2-now1, 3)))
    
print('Tempo total ' + str(round(now2-begin, 3)))