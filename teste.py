import requests

r = requests.get('http://api.olhovivo.sptrans.com.br/v2.1/Login/Autenticar?token=08396f83ad413243052fa0b764c1e1714116a474eceffc7e77cd96d0072c7d87')

print(r.json())