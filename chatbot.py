import streamlit as st
#import openai
from streamlit_chat import message

from decouple import config
import uuid

import pickle
import streamlit_authenticator as stauth
from pathlib import Path
import yaml
from yaml.loader import SafeLoader

#------------------------------------------------------------
openai.api_key = config("OPENAI_API_KEY")
with open('./config.yaml') as file:
    conf = yaml.load(file, Loader=SafeLoader)
authenticator = stauth.Authenticate(
    conf['credentials'],
    conf['cookie']['name'],
    conf['cookie']['key'],
    conf['cookie']['expiry_days'],
    conf['preauthorized']
)

name, authentication_status, username = authenticator.login("Login", "main")
if authentication_status == False:
    st.error("Error en usuario o contraseña")
if authentication_status == None:
    st.warning("Por favor, ingrese usuario y contraseña")

if authentication_status == True:
    session_id = str(uuid.uuid1())  # Genera un identificadxr de sesión único para este usuario
    user_chat_history = session_id + "_chat_history"
    user_generated = session_id + "_generated"
    user_past = session_id + "_past"
    
    if user_chat_history not in st.session_state:
        st.session_state[user_chat_history] = []

    if user_generated not in st.session_state:
        st.session_state[user_generated] = []

    if user_past not in st.session_state:
        st.session_state[user_past] = []

    def generate_response(prompt):
        st.session_state[user_chat_history].append({"role": "system", "content": "Usuario: " + prompt})
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=st.session_state[user_chat_history]
        )
        bot_reply = response.choices[0].message.content
        return bot_reply

    st.title("Herramientas en el Aula")

    user_input = st.text_input("You ", key=session_id)
    submit_button = st.button("Enviar")
    if submit_button and user_input:
        output = generate_response(user_input)
        st.session_state[user_generated].append(output)
        st.session_state[user_past].append(user_input)

    if user_input:
        output = generate_response(user_input)
        st.session_state[user_generated].append(output)
        st.session_state[user_past].append(user_input)

    if st.session_state[user_generated]:
        for i in range(len(st.session_state[user_generated])-1, -1, -1):
            message(st.session_state[user_generated][i], key=str(i))
            message(st.session_state[user_past][i], is_user=True, key=str(i)+'_user')

    st.sidebar.title("Herramientas en el Aula")
    st.sidebar.subheader("Bienvenido equipo " + name)

    authenticator.logout("Logout", "sidebar")
