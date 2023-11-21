import streamlit as st
import openai
from streamlit_chat import message

from decouple import config
import uuid

import streamlit_authenticator as stauth
from pathlib import Path
import yaml
from yaml.loader import SafeLoader

import time

from streamlit_gsheets import GSheetsConnection

#------------------------------------------------------------
#openai.api_key = config("OPENAI_API_KEY")

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

openai.api_key = st.secrets["openai"]["api_key"]
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
    st.caption("Si ya apareció Running y no se actualizó la página, haga click nuevamente en el boton Login")
    st.sidebar.image("https://kit-digital-uc-prod.s3.amazonaws.com/assets/escudos/logo-uc-01.svg", width=200)
    st.sidebar.title("CodeBot Beta")
    st.sidebar.write("CodeBot es un asistente virtual que te ayudará a resolver tus dudas en actividades de programación.")

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
        session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Genera una respuesta del chatbot
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=session_state.chat_history
        )
        bot_reply = response.choices[0].message.content
        session_state.chat_history.append({"role": "system", "content": bot_reply})
        return bot_reply

    def guardar_historial_de_chat(chat_history, username):
        # Guarda el historial del chat en database
        timestamp = int(time.time())
        data = [[username, timestamp]]
        if len(chat_history) > 0:
            for mensaje in chat_history:
                data += [[f"{mensaje['role']}:", f"{mensaje['content']}\n"]]
            conn.create(worksheet=f"{username}_{timestamp}", data=data)
            return
        else:
            return

    st.sidebar.title("CodeBot Beta")
    st.sidebar.write("CodeBot es un asistente virtual que te ayudará a resolver tus dudas en actividades de programación.")
    st.sidebar.header("¡Bienvenid@ " + name + "!")
    
    session_state = get_session_state()

    col1, col2 = st.columns(2)

    with col1:
        st.image("https://kit-digital-uc-prod.s3.amazonaws.com/assets/escudos/logo-uc-01.svg", width=150)

    with col2:
        st.title("CodeBot - Beta")

    
    if 'generated' not in session_state:
        session_state.generated = []

    if 'past' not in st.session_state:
        session_state.past = [] 

    def get_text():
        input_text = st.text_area("Escribe tus consultas ", help="Si ya apreció Running y no se actualizó la página, haga click nuevamente en el boton Enviar")
        return input_text

    user_input = get_text()

    if st.button("Enviar"):
        output = generate_response(user_input)
        session_state.generated.append(output)
        session_state.past.append(user_input)

    st.caption()
   
    if session_state.generated:
        for i in range(len(session_state.generated) - 1, -1, -1):
            message(session_state.generated[i], key=str(i))
            message(session_state.past[i], is_user=True, key=str(i) + '_user')

    # Crear un botón en la barra lateral para eliminar el historial del chat
    if st.sidebar.button("Iniciar nuevo chat"):
        # Llama a la función para guardar el historial del chat
        guardar_historial_de_chat(session_state.chat_history, username)
        st.session_state["chat_history"] = []
        st.session_state['generated'] = []
        st.session_state['past'] = []
        st.rerun()

    st.sidebar.caption("Iniciar nuevo chat, borrará el chat actual y comenzará uno nuevo")


    authenticator.logout("Logout", "sidebar")
    st.sidebar.caption("Para dudas, comentarios o más información escríbenos a cagonzalez24@uc.cl")

    
