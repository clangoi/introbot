import streamlit as st
import openai
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

#------------------------------------------------------------
    def get_session_state():
    # Crea una instancia de SessionState para cada usuario
        session_state = st.session_state
        if not hasattr(session_state, 'chat_history'):
            session_state.chat_history = []
        if not hasattr(session_state, 'generated'):
            session_state.generated = []
        if not hasattr(session_state, 'past'):
            session_state.past = []
        return session_state

    # Define el inicio del chat con el bot
    #chat_history = []

    def generate_response(prompt):
        session_state = get_session_state()
        # Agrega la solicitud al historial del chat en un formato adecuado
        session_state.chat_history.append({"role": "system", "content": "Usuario: " + prompt})
        
        # Genera una respuesta del chatbot
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=session_state.chat_history
        )
        bot_reply = response.choices[0].message.content
        return bot_reply

    session_state = get_session_state()
    st.title("Herramientas en el Aula")

    if 'generated' not in session_state:
        session_state.generated = []

    if 'past' not in st.session_state:
        session_state.past = [] 

    def get_text():
        input_text = st.text_input("You ", key='input')
        return input_text

    user_input = get_text()

    if user_input:
        output = generate_response(user_input)
        session_state.generated.append(output)
        session_state.past.append(user_input)

    if session_state.generated:
        for i in range(len(session_state.generated) - 1, -1, -1):
            message(session_state.generated[i], key=str(i))
            message(session_state.past[i], is_user=True, key=str(i) + '_user')

    st.sidebar.title("Herramientas en el Aula")
    st.sidebar.subheader("Bienvenido equipo " + name)

    authenticator.logout("Logout", "sidebar")
