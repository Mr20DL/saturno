import requests

url = "https://openlibrary.org/search.json?q=python"

respuesta = requests.get(url)

datos = respuesta.json()
for libro in datos["docs"][:10]:
    print(libro["title"])
