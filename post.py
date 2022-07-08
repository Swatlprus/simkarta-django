import requests
from requests.auth import HTTPBasicAuth

# подготовка параметров для POST-запроса
param = {'login': 'gilmiiarov.ra', 'password': 'T7YPgQcoqs'}
# обратите внимание, что для метода POST, аргумент для
# передачи параметров в запрос отличается от метода GET
#resp = requests.post("https://hr.domru.ru/mira/service/v2/auth/login", data=param)
#print(resp.text)

# Данные для авторизации
auth = HTTPBasicAuth('gilmiiarov.ra', 'T7YPgQcoqs')

# создаем GET запрос
fullReq = requests.get('https://hr.domru.ru/mira/service/v2/persons/331051', data=param,
                       auth=auth).json()

print(fullReq)