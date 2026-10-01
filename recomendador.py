import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ============================================================
# 1. Cargar candidatos
# ============================================================
with open("candidatos.json", "r", encoding="utf-8") as f:
    candidatos = json.load(f)

# ============================================================
# 2. Definir perfil del usuario
# ============================================================
perfil = "artificial intelligence programming databases python machine learning"

intereses_usuario = [
    "artificial intelligence",
    "programming",
    "sql",
    "python",
    "machine learning"
]

# ============================================================
# 3. Construir documentos para cada libro
# ============================================================
documentos = []
for libro in candidatos:
    texto = libro["titulo"] + " " + " ".join(libro["subjects"])
    documentos.append(texto)

# ============================================================
# 4. Vectorizar con TF-IDF
# ============================================================
vectorizador = TfidfVectorizer()
matriz_libros = vectorizador.fit_transform(documentos)
vector_perfil = vectorizador.transform([perfil])

# ============================================================
# 5. Calcular similitud coseno
# ============================================================
similitudes = cosine_similarity(vector_perfil, matriz_libros).flatten()
indices_ordenados = similitudes.argsort()[::-1]

N = 5

# ============================================================
# 6. Función auxiliar: mostrar Top-N
# ============================================================
def mostrar_top(indices, titulo):
    print(f"\n{titulo}\n")
    for i in indices[:N]:
        libro = candidatos[i]
        autores = ", ".join(libro["autores"]) if libro["autores"] else "No disponible"
        print(f"Título: {libro['titulo']}")
        print(f"Autores: {autores}")
        print(f"Similitud: {similitudes[i]:.4f}")
        print(f"Materias: {', '.join(libro['subjects'][:5])}")
        print("-" * 60)

# ============================================================
# 7. Función de cobertura de intereses
# ============================================================
def calcular_cobertura(indices, N):
    top_n = [candidatos[i] for i in indices[:N]]
    cobertura_por_interes = {}

    print(f"\nCobertura de intereses en el Top-{N}:")
    print("-" * 50)

    for interes in intereses_usuario:
        palabras = interes.lower().split()
        count = 0
        for libro in top_n:
            texto = (libro["titulo"] + " " + " ".join(libro["subjects"])).lower()
            if all(p in texto for p in palabras):
                count += 1
        cobertura_por_interes[interes] = count
        print(f"  {interes}: {count}/{N}  ({count/N:.0%})")

    cobertura_global = sum(cobertura_por_interes.values()) / (len(intereses_usuario) * N)
    ausentes = [i for i, c in cobertura_por_interes.items() if c == 0]

    print(f"\nCobertura global ponderada: {cobertura_global:.2%}")
    print(f"Intereses ausentes: {ausentes if ausentes else 'Ninguno'}")

    return cobertura_global, ausentes

# ============================================================
# 8. Función de diversificación (mitigación de sesgo)
# ============================================================
def top_n_diversificado(candidatos, similitudes, N=5, penalizacion=0.7):
    indices = list(range(len(candidatos)))
    seleccionados = []
    materias_usadas = set()

    while len(seleccionados) < N and indices:
        mejor_idx = None
        mejor_score = -1

        for i in indices:
            materias_libro = set(candidatos[i]["subjects"])
            if materias_usadas:
                solapamiento = len(materias_libro & materias_usadas) / max(len(materias_libro), 1)
            else:
                solapamiento = 0
            score = similitudes[i] * (1 - penalizacion * solapamiento)
            if score > mejor_score:
                mejor_score = score
                mejor_idx = i

        seleccionados.append(mejor_idx)
        materias_usadas |= set(candidatos[mejor_idx]["subjects"])
        indices.remove(mejor_idx)

    return seleccionados

# ============================================================
# 9. Comparación: Top-N original vs Top-N diversificado
# ============================================================

print("=" * 60)
print("RECOMENDACIÓN SIN DIVERSIFICAR (basada solo en similitud)")
print("=" * 60)

mostrar_top(indices_ordenados, f"Top {N} original:")
cob_original, ausentes_original = calcular_cobertura(indices_ordenados, N)

print("\n\n")
print("=" * 60)
print("RECOMENDACIÓN CON DIVERSIFICACIÓN (mitigación de sesgo)")
print("=" * 60)

indices_diversificados = top_n_diversificado(candidatos, similitudes, N=N, penalizacion=0.7)

mostrar_top(indices_diversificados, f"Top {N} diversificado:")
cob_diversificada, ausentes_div = calcular_cobertura(indices_diversificados, N)

# ============================================================
# 10. Resumen comparativo
# ============================================================
print("\n\n")
print("=" * 60)
print("RESUMEN COMPARATIVO")
print("=" * 60)
print(f"Cobertura original:      {cob_original:.2%}  |  Ausentes: {ausentes_original}")
print(f"Cobertura diversificada: {cob_diversificada:.2%}  |  Ausentes: {ausentes_div}")

# ============================================================
# 11. Métrica de relevancia percibida (proxy)
# ============================================================
def relevancia_percibida(indices, N, umbral=0.2):
    top_n_sim = [similitudes[i] for i in indices[:N]]
    promedio = sum(top_n_sim) / len(top_n_sim)
    sobre_umbral = sum(1 for s in top_n_sim if s > umbral)
    print(f"\nRelevancia percibida (proxy):")
    print(f"  Similitud promedio Top-{N}: {promedio:.4f}")
    print(f"  Libros con similitud > {umbral}: {sobre_umbral}/{N} ({sobre_umbral/N:.0%})")
    return promedio, sobre_umbral

print("\n\n")
print("=" * 60)
print("MÉTRICA DE RELEVANCIA PERCIBIDA")
print("=" * 60)

print("\nSin diversificar:")
rel_orig = relevancia_percibida(indices_ordenados, N)

print("\nDiversificado:")
rel_div = relevancia_percibida(indices_diversificados, N)