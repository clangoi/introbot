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

import os
import time



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
        session_state.chat_history.append({"role": "user", "content": "Usuario: " + prompt})
        
        # Genera una respuesta del chatbot
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=session_state.chat_history
        )
        bot_reply = response.choices[0].message.content
        session_state.chat_history.append({"role": "system", "content": "Bot: " + bot_reply})
        return bot_reply

    def guardar_historial_de_chat(chat_history, username):
        # Genera un nombre de archivo único con el nombre de usuario y el timestamp
        timestamp = int(time.time())
        archivo_nombre = f"{username}_{timestamp}.txt"
        
        # Ruta donde se guardarán los archivos de historial
        carpeta_historial = "./historiales_de_chat"
        
        # Crea la carpeta si no existe
        if not os.path.exists(carpeta_historial):
            os.makedirs(carpeta_historial)
        
        # Guarda el historial del chat en el archivo
        with open(os.path.join(carpeta_historial, archivo_nombre), "w") as archivo:
            for mensaje in chat_history:
                archivo.write(f"{mensaje['role']}: {mensaje['content']}\n")

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

     # Crear un botón en la barra lateral para eliminar el historial del chat
    if st.sidebar.button("Borrar Historial de Chat"):
        # Llama a la función para guardar el historial del chat
        guardar_historial_de_chat(session_state.chat_history, username)
        chat_history = []
        user_input = ""
        st.session_state['generated'] = []
        st.session_state['past'] = []
        st.sidebar.write("Chat borrado")

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
