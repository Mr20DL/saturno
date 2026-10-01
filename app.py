import json
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="Recomendador de Libros", page_icon="📚", layout="wide")

st.title("📚 Recomendador de Libros para Estudiantes")
st.caption("Basado en Open Library API + TF-IDF + similitud coseno")

# ============================================================
# Cargar candidatos
# ============================================================
@st.cache_data
def cargar_candidatos():
    with open("candidatos.json", "r", encoding="utf-8") as f:
        return json.load(f)

candidatos = cargar_candidatos()

# ============================================================
# Sidebar: perfil del usuario
# ============================================================
st.sidebar.header("🎓 Perfil del usuario")

carrera = st.sidebar.text_input("Carrera", "Ingeniería de Software")
nivel = st.sidebar.selectbox("Nivel", ["Básico", "Intermedio", "Avanzado"], index=1)

intereses_disponibles = [
    "artificial intelligence",
    "machine learning",
    "programming",
    "python",
    "sql",
    "databases",
    "computer science"
]

intereses_seleccionados = st.sidebar.multiselect(
    "Intereses",
    intereses_disponibles,
    default=["artificial intelligence", "programming", "python", "sql"]
)

interes_libre = st.sidebar.text_input(
    "Añadir interés personalizado (ej: cocina, astronomía)",
    ""
).strip().lower()

if interes_libre:
    intereses_seleccionados = list(intereses_seleccionados) + [interes_libre]


N = st.sidebar.slider("Tamaño del Top-N", min_value=3, max_value=10, value=5)

usar_diversificacion = st.sidebar.checkbox(
    "Aplicar diversificación (mitigación de sesgo)",
    value=True
)

# ============================================================
# Botón para recomendar
# ============================================================
if st.sidebar.button("🔍 Generar recomendaciones", type="primary"):
    if not intereses_seleccionados:
        st.warning("Selecciona al menos un interés.")
        st.stop()

    perfil = " ".join(intereses_seleccionados)

    # Construir documentos
    documentos = [
        libro["titulo"] + " " + " ".join(libro["subjects"])
        for libro in candidatos
    ]

    # TF-IDF
    vectorizador = TfidfVectorizer()
    matriz_libros = vectorizador.fit_transform(documentos)
    vector_perfil = vectorizador.transform([perfil])

    # Similitud
    similitudes = cosine_similarity(vector_perfil, matriz_libros).flatten()
    indices_ordenados = similitudes.argsort()[::-1]

    # ============================================================
    # Diversificación
    # ============================================================
    def top_n_diversificado(candidatos, similitudes, N, penalizacion=0.7):
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

    indices_finales = (
        top_n_diversificado(candidatos, similitudes, N)
        if usar_diversificacion
        else indices_ordenados[:N]
    )

    # ============================================================
    # Mostrar resultados
    # ============================================================
    st.subheader(f"Top-{N} recomendaciones para {carrera} ({nivel})")
    st.markdown(f"**Intereses:** {', '.join(intereses_seleccionados)}")

    # Filtrar libros sin similitud real
    indices_finales_filtrados = [i for i in indices_finales if similitudes[i] > 0.01]

    if not indices_finales_filtrados:
        st.error("⚠️ No se encontraron libros relevantes para los intereses seleccionados.")
        st.info("El catálogo actual no contiene libros relacionados con esos temas. "
                "Prueba con otros intereses o amplía la base de candidatos.")
    else:        
        for rank, i in enumerate(indices_finales, start=1):
            libro = candidatos[i]
            autores = ", ".join(libro["autores"]) if libro["autores"] else "No disponible"
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### {rank}. {libro['titulo']}")
                    st.markdown(f"**Autores:** {autores}")
                    st.markdown(f"**Materias:** {', '.join(libro['subjects'][:6])}")
                with col2:
                    st.metric("Similitud", f"{similitudes[i]:.3f}")

    # ============================================================
    # Métricas
    # ============================================================
    st.divider()
    st.subheader("📊 Métricas del sistema")

    top_n = [candidatos[i] for i in indices_finales]

    # Cobertura
    cobertura = {}
    for interes in intereses_seleccionados:
        palabras = interes.lower().split()
        count = sum(
            1 for libro in top_n
            if all(p in (libro["titulo"] + " " + " ".join(libro["subjects"])).lower() for p in palabras)
        )
        cobertura[interes] = count

    cob_global = sum(cobertura.values()) / (len(intereses_seleccionados) * N)
    ausentes = [i for i, c in cobertura.items() if c == 0]

    # Relevancia
    relevancia_prom = sum(similitudes[i] for i in indices_finales) / N

    col1, col2, col3 = st.columns(3)
    col1.metric("Cobertura global", f"{cob_global:.2%}")
    col2.metric("Relevancia promedio", f"{relevancia_prom:.3f}")
    col3.metric("Intereses ausentes", len(ausentes))

    with st.expander("Ver cobertura por interés"):
        for interes, count in cobertura.items():
            st.write(f"- **{interes}**: {count}/{N} ({count/N:.0%})")

    if ausentes:
        st.warning(f"⚠️ Intereses sin representación: {', '.join(ausentes)}")
    else:
        st.success("✅ Todos los intereses están representados en el Top-N.")

else:
    st.info("👈 Configura tu perfil en la barra lateral y presiona **Generar recomendaciones**.")