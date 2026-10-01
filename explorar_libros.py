import requests
import time

terminos= ["python", "inteligencia artificial", "bases de datos"]

for termino in terminos:
    url = "https://openlibrary.org/search.json"
    params = {
        "q": termino,
        "limit": 5
    }

    respuesta = requests.get(url, params=params)

    print("=" * 60)
    print("Término de búsqueda:", termino)
    print("Status code:", respuesta.status_code)

    datos = respuesta.json()

    print("Resultados encontrados:", datos.get("numFound"))

    for libro in datos.get("docs", [])[:5]:
        print("-" * 40)
        print("Titulo:", libro.get("title"))
        print("Autores:", libro.get("author_name", ["No disponible"]))
        print("Año primera publicación:", libro.get("first_publish_year", "No disponible"))
        print("Materias:", libro.get("subject", [])[:5])
        print("Idiomas:", libro.get("language", ["No disponible"]))
        print("Ediciones:", libro.get("edition_count", "No disponible"))
        print("Key:", libro.get("key"))

    time.sleep(1)
