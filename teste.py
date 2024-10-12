import pandas as pd
from sptrans import SPTransClient

token = '08396f83ad413243052fa0b764c1e1714116a474eceffc7e77cd96d0072c7d87'

api = SPTransClient()
auth = api.auth(token)

# ${url}Login/Autenticar?token=${token}

if auth:
    response = api.get_bus_position()

    df = pd.json_normalize(response['l'])

    print(df)
else:
    print('Autenticação Inválida')