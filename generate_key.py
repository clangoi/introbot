# import pickle
# from pathlib import Path

# import streamlit_authenticator as stauth


# names = ["peter", "paul", "mary"]
# passwords = ["123", "456", "789"]
# usernames = ["peter", "paul", "mary"]

# hashed_passwords = stauth.Hasher(passwords).generate()

# file_path = Path(__file__).parent / "config.yaml"
# with open(file_path, "wb") as f:
#     pickle.dump(hashed_passwords, f)


import pickle
from pathlib import Path
import yaml
import streamlit_authenticator as stauth

# Datos de usuarios
names = ["peter", "paul", "mary"]
passwords = ["123", "456", "789"]
usernames = ["peter", "paul", "mary"]

# Genera contraseñas hasheadas
hashed_passwords = stauth.Hasher(passwords).generate()

# Crear diccionario de credenciales
credentials = {}
for name, username, password in zip(names, usernames, hashed_passwords):
    credentials[username] = {
        "password": password,
        "name": name
    }

# Crear diccionario de configuración
config_data = {
    "credentials": {
        "usernames": credentials
    },
    "cookie": {
        "name": "hola",
        "key": "key",
        "expiry_days": 0
    },
    "preauthorized": {
        "usernames": usernames
    }
}

# Ruta al archivo de configuración
file_path = Path(__file__).parent / "config.yaml"

# Guardar el diccionario en el archivo YAML
with open(file_path, "w") as f:
    yaml.dump(config_data, f, default_flow_style=False)