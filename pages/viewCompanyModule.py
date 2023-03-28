import time
import folium as fo
from streamlit_folium import folium_static
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import plotly.express as px
import streamlit as st

begin = time.time()

st.set_page_config(page_title='Visão Empresa', layout='wide')

# Funções:
def clearCode(df1):
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
  
  return df1

def orderMetric(df1):
  dfAux = df1.loc[:, ['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()
  return px.bar(dfAux, y='ID', x='Order_Date')

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

df1 = clearCode(df1)
now2 = time.time()
print('Limpeza feita ' + str(round(now2-now1, 3)))

# Streamlit
# Barra lateral
# st.dataframe(df1)
st.header('Marketplace Visão Cliente')
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

# Layout principal
tab1, tab2, tab3 = st.tabs(['Visão Estratégica', 'Visão Tática', 'Visão Geográfica'])
with tab1:
  with st.container():
    # Quantidade de pedidos por dia, gráfico de barras.
    # Se não fizer o reset_index abaixo, ele transforma a coluna de agrupamento em índice,
    # perdendo a possibilidade de referenciá-la de outra forma.
    st.markdown('## Orders by Day')
    st.plotly_chart(orderMetric(df1), use_container_width=True)
    now1 = now2
    now2 = time.time()
    print('px.bar gerado ' + str(round(now2-now1, 3)))
  with st.container():
    col1, col2 = st.columns(2)
    with col1:
      # Distribuição dos pedidos por tipo de tráfego, gráfico de pizza.
      st.markdown('### Orders by Traffic')
      dfAux = df1.loc[df1['Road_traffic_density']!='NaN',
                      ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
      dfAux['Percentual'] = dfAux['ID']/dfAux['ID'].sum()
      st.plotly_chart(px.pie(dfAux, values='Percentual', names='Road_traffic_density'), use_container_width=True)
      now1 = now2
      now2 = time.time()
      print('px.pie gerado ' + str(round(now2-now1, 3)))
    with col2:
      # Comparação do volume de pedidos por cidade e tipo de tráfego, gráfico de bolhas.
      st.markdown('### Orders by City and Traffic')
      dfAux = df1.loc[(df1['Road_traffic_density']!='NaN') & (df1['City']!='NaN'), ['ID', 'City', 'Road_traffic_density']]
      dfAux = dfAux.groupby(['City', 'Road_traffic_density']).count().reset_index()
      dfAux.rename(columns={'ID': 'Qtd_Pedidos'}, inplace=True)
      fig = px.scatter(dfAux, x='City', y='Road_traffic_density', size='Qtd_Pedidos', color='City')
      st.plotly_chart(fig, use_container_width=True)
      now1 = now2
      now2 = time.time()
      print('px.scatter gerado ' + str(round(now2-now1, 3)))

with tab2:
  with st.container():
    # 2. Quantidade de pedidos por semana, gráfico de linha.
    st.markdown('## Weekly Orders')
    dfAux = df1.loc[:, ['ID', 'Order_Date']]
    dfAux['week_number'] = dfAux['Order_Date'].dt.strftime('%U')
    dfAux = dfAux.drop('Order_Date', 1) # Não precisa, só para deixar mais limpo.
    dfAux.rename(columns={'ID': 'Qtd_Pedidos'}, inplace=True)
    dfAux = dfAux.groupby('week_number').count().reset_index()
    st.plotly_chart(px.line(dfAux, x='week_number', y='Qtd_Pedidos'), use_container_width=True)
    now1 = now2
    now2 = time.time()
    print('px.line 1 gerado ' + str(round(now2-now1, 3)))
  with st.container():
    # 5. A quantidade de pedidos por entregador por semana, gráfico de linha.
    st.markdown('## Weekly Orders by Person')
    dfAux = df1.loc[:, ['ID', 'Delivery_person_ID', 'Order_Date']]
    dfAux['week_number'] = dfAux['Order_Date'].dt.strftime('%U')
    dfAux1 = dfAux.loc[:, ['ID', 'week_number']].groupby('week_number').count().reset_index()
    dfAux2 = dfAux.loc[:, ['Delivery_person_ID', 'week_number']].groupby('week_number').nunique().reset_index()
    dfAux = pd.merge(dfAux1, dfAux2, how='inner')
    dfAux.rename(columns={'ID': 'Qtd_Pedidos', 'Delivery_person_ID': 'Qtd_Entregadores'}, inplace=True)
    dfAux['Pedidos_por_entregador'] = dfAux['Qtd_Pedidos']/dfAux['Qtd_Entregadores']
    st.plotly_chart(px.line(dfAux, x='week_number', y='Pedidos_por_entregador'), use_container_width=True)
    now1 = now2
    now2 = time.time()
    print('px.line 2 gerado ' + str(round(now2-now1, 3)))

with tab3:
  # A localização central de cada cidade por tipo de tráfego.
  st.markdown('## Central Location by Traffic')
  dfDataPlot = df1.loc[(df1['Road_traffic_density']!='NaN') & (df1['City']!='NaN'),
                       ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']]
  dfDataPlot = dfDataPlot.groupby(['City', 'Road_traffic_density']).median().reset_index()
  map = fo.Map(zoom_start=17)
  for i, ponto in dfDataPlot.iterrows():
    if ponto['Road_traffic_density']=='High':
      ponto['color'] = 'red'
    elif ponto['Road_traffic_density']=='Jam':
      ponto['color'] = 'orange'
    elif ponto['Road_traffic_density']=='Medium':
      ponto['color'] = 'blue'
    elif ponto['Road_traffic_density']=='Low':
      ponto['color'] = 'green'
    fo.Marker([ponto['Delivery_location_latitude'], ponto['Delivery_location_longitude']],
              popup=ponto['City'] + '\n' + ponto['Road_traffic_density'],
              icon=fo.Icon(color=ponto['color'])).add_to(map)
  sw = dfDataPlot[['Delivery_location_latitude', 'Delivery_location_longitude']].min().values.tolist()
  ne = dfDataPlot[['Delivery_location_latitude', 'Delivery_location_longitude']].max().values.tolist()
  map.fit_bounds([sw, ne])
  folium_static(map, height=1024, width=600)
  now1 = now2
  now2 = time.time()
  print('map gerado ' + str(round(now2-now1, 3)))


print('Tempo total ' + str(round(now2-begin, 3)))
