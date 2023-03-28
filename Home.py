import streamlit as st
from PIL import Image

st.set_page_config(page_title='Home', layout='wide')

st.sidebar.image(Image.open('pineapple.jpg'), width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")
st.write("Curry Company Growth Dashboard")