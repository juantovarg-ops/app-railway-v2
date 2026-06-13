import streamlit as st
import os
from dotenv import load_dotenv

from db_sql import init_sql, log_search, get_search_stats
from db_mongo import init_mongo, upsert_product, get_product_by_id
from db_qdrant import init_qdrant, index_product, semantic_search
from ai import get_embedding, generate_summary, seed_products

load_dotenv()

# Init all services
init_sql()
init_mongo()
init_qdrant()

st.set_page_config(page_title="Smart Product Search", page_icon="🔍", layout="wide")
st.title("🔍 Smart Product Search")
st.caption("Búsqueda semántica con PostgreSQL + MongoDB + Redis + Qdrant + IA")

# Sidebar — seed & stats
with st.sidebar:
    st.header("⚙️ Admin")
    if st.button("🌱 Seed productos demo", use_container_width=True):
        with st.spinner("Indexando productos..."):
            count = seed_products(upsert_product, index_product, get_embedding)
        st.success(f"{count} productos indexados")

    st.divider()
    st.subheader("📊 Estadísticas")
    stats = get_search_stats()
    for row in stats:
        st.metric(label=row[0], value=row[1])

# Search UI
col1, col2 = st.columns([4, 1])
with col1:
    query = st.text_input(
        "Busca productos en lenguaje natural",
        placeholder="ej: algo para cocinar arroz rápido, bebida sin azúcar para deportistas..."
    )
with col2:
    top_k = st.selectbox("Resultados", [3, 5, 10], index=1)

if query:
    with st.spinner("Buscando..."):
        # 1. Embed query
        query_vec = get_embedding(query)
        # 2. Semantic search in Qdrant
        hits = semantic_search(query_vec, top_k=top_k)
        # 3. Fetch full docs from MongoDB
        products = [get_product_by_id(h.id) for h in hits]
        products = [p for p in products if p]
        # 4. Log to PostgreSQL
        log_search(query, len(products))

    if not products:
        st.warning("Sin resultados. Prueba con el botón **Seed productos demo** en el sidebar.")
    else:
        # AI summary
        with st.spinner("Generando resumen IA..."):
            summary = generate_summary(query, products)

        st.info(f"🤖 **IA dice:** {summary}")
        st.divider()

        cols = st.columns(min(len(products), 3))
        for i, (prod, hit) in enumerate(zip(products, hits)):
            with cols[i % 3]:
                score = round(hit.score * 100, 1)
                st.markdown(f"### {prod.get('name', 'N/A')}")
                st.markdown(f"**Categoría:** {prod.get('category', '-')}")
                st.markdown(f"**Precio:** S/ {prod.get('price', 0):.2f}")
                st.markdown(f"**Stock:** {prod.get('stock', 0)} u.")
                st.markdown(f"**Relevancia:** `{score}%`")
                st.markdown(f"_{prod.get('description', '')}_")
                st.divider()
