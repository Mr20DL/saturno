import requests
import time
import json

# Perfil del usuario (intereses en inglés para mejor cobertura)
intereses = [
    "artificial intelligence",
    "programming",
    "sql",
    "python"
]

candidatos = []
keys_vistas = set()

for interes in intereses:
    print(f"Buscando: {interes}...")
    url = "https://openlibrary.org/search.json"
    params = {
        "q": interes,
        "limit": 15  # más resultados para filtrar
    }
    respuesta = requests.get(url, params=params)
    datos = respuesta.json()

    for libro in datos.get("docs", []):
        key = libro.get("key")
        if not key or key in keys_vistas:
            continue
        keys_vistas.add(key)

        # Obtener detalle para subjects
        url_detalle = "https://openlibrary.org" + key + ".json"
        resp_detalle = requests.get(url_detalle)
        if resp_detalle.status_code != 200:
            continue
        detalle = resp_detalle.json()

        subjects = detalle.get("subjects", [])
        if not subjects:
            # Si no hay subjects, saltamos este libro
            continue

        # Normalizamos subjects a minúsculas
        subjects = [s.lower() for s in subjects]

        # Autores: usamos author_name del resultado de búsqueda
        autores = libro.get("author_name", [])

        titulo = libro.get("title", "Sin título")

        candidatos.append({
            "key": key,
            "titulo": titulo,
            "autores": autores,
            "subjects": subjects,
            "interes_buscado": interes
        })

        time.sleep(0.3)  # pausa para no saturar

print(f"\nTotal de candidatos únicos con subjects: {len(candidatos)}")
for c in candidatos[:10]:
    print("-" * 50)
    print("Título:", c["titulo"])
    print("Autores:", c["autores"])
    print("Materias (primeras 5):", c["subjects"][:5])
    print("Buscado por:", c["interes_buscado"])

with open("candidatos.json", "w", encoding="utf-8") as f:
    json.dump(candidatos, f, ensure_ascii=False, indent=2)

print("\nGuardado en candidatos.json")