# Intereses del usuario como lista
intereses_usuario = [
    "artificial intelligence",
    "programming",
    "databases",
    "python",
    "machine learning"
]

# Tomamos el Top-N que ya calculamos
N = 5
top_n = [candidatos[i] for i in indices_ordenados[:N]]

# Para cada interés, contamos cuántos libros del Top-N lo cubren
print("\nCobertura de intereses en el Top-5:")
print("-" * 50)

for interes in intereses_usuario:
    palabras_interes = interes.lower().split()
    count = 0
    for libro in top_n:
        # Unimos título + materias en un solo texto
        texto_libro = (libro["titulo"] + " " + " ".join(libro["subjects"])).lower()
        # Contamos si TODAS las palabras del interés aparecen
        if all(p in texto_libro for p in palabras_interes):
            count += 1
    print(f"  {interes}: {count} de {N} libros")

# Cobertura global: fracción de intereses con al menos 1 libro
intereses_cubiertos = 0
for interes in intereses_usuario:
    palabras_interes = interes.lower().split()
    for libro in top_n:
        texto_libro = (libro["titulo"] + " " + " ".join(libro["subjects"])).lower()
        if all(p in texto_libro for p in palabras_interes):
            intereses_cubiertos += 1
            break

cobertura = intereses_cubiertos / len(intereses_usuario)
print(f"\nCobertura global: {cobertura:.2%} ({intereses_cubiertos}/{len(intereses_usuario)} intereses)")