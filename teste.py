from sptrans import SPTransClient

token = '08396f83ad413243052fa0b764c1e1714116a474eceffc7e77cd96d0072c7d87'

api = SPTransClient()
auth = api.auth(token)

if auth:
    response = api.get_bus_position()

    print(response)
else:
    print('Autenticação Inválida')