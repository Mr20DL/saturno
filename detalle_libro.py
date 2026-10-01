import requests

key = "/works/OL2784125W"  # Learning Python
url = "https://openlibrary.org" + key + ".json"

respuesta = requests.get(url)
print("Status:", respuesta.status_code)

datos = respuesta.json()

print("Claves disponibles:", list(datos.keys()))
print("Título:", datos.get("title"))
print("Materias:", datos.get("subjects", []))
print("Descripción:", datos.get("description", "No disponible"))