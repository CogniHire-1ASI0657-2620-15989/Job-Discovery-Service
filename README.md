# Job-Search Service

Microservicio horientado a la búsqueda de empleo y favoritos. Consume exclusivamente la API de Jooble Perú y confía en un API Gateway para autenticar al usuario.

## Configuración

1. Copia `.env.example` a `.env` y completa las cuatro variables. `JOOBLE_API_KEY` se obtiene en el portal de Jooble Perú; no la subas al repositorio.
2. Crea una base PostgreSQL dedicada, por ejemplo `job_search_db`.
3. Instala las dependencias y ejecuta las migraciones:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## Seguridad de red

El servicio **no valida JWT**. Debe estar expuesto solo al API Gateway, que valida el token y reenvía un encabezado `X-User-Id` (configurable). Una llamada directa sin ese encabezado recibe `401`.

## Endpoints

- `GET /health`
- `GET /api/v1/jobs?keywords=python&location=Lima&page=1&page_size=10&radius_km=0`
- `GET /api/v1/jobs/{job_id}`
- `POST /api/v1/jobs/{job_id}/favorite`
- `DELETE /api/v1/jobs/{job_id}/favorite`
- `GET /api/v1/favorites?page=1&page_size=20`

Las búsquedas que no pueden llegar a Jooble por timeout, error HTTP o circuit breaker devuelven `200` con `items: []` y `provider_status: "unavailable"`.

## Límites de resultados

Para preservar la cuota de Jooble y evitar una navegación ilimitada, la búsqueda permite como máximo tres páginas. `page_size` es `10` por defecto y admite hasta `20`. El campo `total` se limita a los resultados realmente navegables: hasta `30` con el tamaño por defecto y hasta `60` con `page_size=20`.
