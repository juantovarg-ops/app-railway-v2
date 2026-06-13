# 🔍 Smart Product Search

Búsqueda semántica de productos usando stack completo:
**PostgreSQL + MongoDB + Redis + Qdrant + Gemini AI**

## Arquitectura

```
Usuario
  │
  ▼
Streamlit (app.py)
  │
  ├── PostgreSQL  → Logs de búsquedas (audit trail relacional)
  ├── MongoDB     → Catálogo de productos (documentos flexibles)
  ├── Redis       → Cache de embeddings (TTL 24h)
  ├── Qdrant      → Índice vectorial (búsqueda semántica)
  └── Gemini AI   → Embeddings (text-embedding-004) + Resumen (gemini-2.0-flash)
```

## Flujo de una búsqueda

1. Usuario escribe query en lenguaje natural
2. Gemini genera embedding del query (o lo recupera de Redis si ya fue cacheado)
3. Qdrant busca los K vectores más cercanos → devuelve `product_id`s con score
4. MongoDB recupera los documentos completos por `product_id`
5. Gemini genera recomendación textual basada en resultados
6. PostgreSQL registra la búsqueda para estadísticas

## Setup local

```bash
cp .env.example .env
# Edita .env con tu GEMINI_API_KEY

docker compose up --build
```

App disponible en http://localhost:8501

1. Abre el sidebar → **Seed productos demo**
2. Busca: *"algo para cocinar arroz rápido"* o *"bebida sin azúcar para deportistas"*

## Deploy en Railway

### Paso 1 — Crear servicios desde el dashboard

En tu proyecto Railway, agrega estos servicios desde **+ New**:

| Servicio | Template Railway | Variable que expone |
|----------|-----------------|---------------------|
| PostgreSQL | Database → PostgreSQL | `DATABASE_URL` |
| MongoDB | Database → MongoDB | `MONGO_URL` |
| Redis | Database → Redis | `REDIS_URL` |
| Qdrant | Docker Image → `qdrant/qdrant` | configura manual |

### Paso 2 — Configurar Qdrant en Railway

En el servicio Qdrant:
- **Image**: `qdrant/qdrant`
- **Port**: `6333`
- Agrega variable `QDRANT_API_KEY` con un valor aleatorio seguro
- Copia el dominio interno generado (ej: `qdrant.railway.internal:6333`)

### Paso 3 — Deploy de la app

```bash
# Conecta tu repo a Railway
railway link

# O desde GitHub: New Project → Deploy from GitHub repo
```

### Paso 4 — Variables de entorno en la app

En el servicio de la app, Railway inyecta `DATABASE_URL`, `MONGO_URL` y `REDIS_URL`
automáticamente si están en el mismo proyecto. Agrega manualmente:

```
MONGO_DB=smartsearch
QDRANT_URL=http://qdrant.railway.internal:6333
QDRANT_API_KEY=<el valor que pusiste en el servicio Qdrant>
GEMINI_API_KEY=<tu API key de Google AI Studio>
```

### Paso 5 — Verificar

```bash
railway logs
```

Busca `You can now view your Streamlit app in your browser` y abre el dominio público.

## Estructura del proyecto

```
.
├── app.py          # UI Streamlit + orquestación
├── db_sql.py       # PostgreSQL: logs de búsqueda
├── db_mongo.py     # MongoDB: catálogo de productos
├── db_qdrant.py    # Qdrant: índice vectorial
├── ai.py           # Gemini: embeddings + generación + seed data
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Variables de entorno requeridas

| Variable | Descripción |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `MONGO_URL` | MongoDB connection string |
| `MONGO_DB` | Nombre de la base de datos MongoDB (default: `smartsearch`) |
| `REDIS_URL` | Redis connection string |
| `QDRANT_URL` | URL del servidor Qdrant |
| `QDRANT_API_KEY` | API key de Qdrant (vacío si sin auth) |
| `GEMINI_API_KEY` | Google AI Studio API key |
