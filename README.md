# Job-Search Service

Microservicio de búsqueda de empleo y favoritos. Consume exclusivamente la API de Jooble Perú, cachea resultados en Redis y confía en un API Gateway para autenticar al usuario.

## Configuración

1. Copia `.env.example` a `.env` y completa las variables:
   - `DATABASE_URL`, `DATABASE_SCHEMA`: conexión a la base PostgreSQL dedicada (ej. `job_search_db`).
   - `JOOBLE_API_KEY`, `JOOBLE_BASE_URL`: credenciales de Jooble Perú (se obtienen en el portal de Jooble Perú; no subas la key al repositorio).
   - `GATEWAY_USER_ID_HEADER`: nombre del header que inyecta el API Gateway con el id del usuario autenticado (por defecto `X-User-Id`).
   - `INTERNAL_API_KEY`: secreto compartido que debe enviar el Gateway en `X-Internal-Api-Key` en **todas** las peticiones (ver "Seguridad de red").
   - `REDIS_URL` (opcional, no viene en `.env.example`): si se define, habilita el caché de búsquedas. Si se omite, el servicio funciona igual pero sin cachear.
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

El servicio **no valida JWT**: esa responsabilidad es del API Gateway. Debe estar expuesto solo al Gateway, que:

- valida el token del usuario y reenvía su id en el header configurable `X-User-Id` (`GATEWAY_USER_ID_HEADER`);
- reenvía el secreto compartido en `X-Internal-Api-Key`.

Un middleware global exige `X-Internal-Api-Key` en **todas las rutas excepto `/health`**; sin ese header, cualquier llamada directa recibe `401 Unauthorized` (`application/problem+json`). Una llamada sin `X-User-Id` en una ruta que lo requiere también falla.

## Endpoints

- `GET /health`
- `GET /api/v1/jobs?keywords=python&location=Lima&page=1&page_size=10&radius_km=0`
- `GET /api/v1/jobs/{job_id}`
- `POST /api/v1/jobs/{job_id}/favorite`
- `DELETE /api/v1/jobs/{job_id}/favorite`
- `GET /api/v1/favorites?page=1&page_size=20`
- `GET /api/v1/internal/favorites/{job_id}` — uso interno entre microservicios (ej. Gap Analysis); requiere `X-User-Id` + `X-Internal-Api-Key`, devuelve `404` si el usuario no tiene esa vacante en favoritos.

Las búsquedas que no pueden llegar a Jooble por timeout, error HTTP o circuit breaker devuelven `200` con `items: []` y `provider_status: "unavailable"`.

## Límites de resultados

Para preservar la cuota de Jooble y evitar una navegación ilimitada, la búsqueda permite como máximo tres páginas. `page_size` es `10` por defecto y admite hasta `20`. El campo `total` se limita a los resultados realmente navegables: hasta `30` con el tamaño por defecto y hasta `60` con `page_size=20`.

## Caché de búsquedas (Redis)

Si `REDIS_URL` está configurado, cada búsqueda (`GET /api/v1/jobs`) se cachea por 10 minutos usando como clave los parámetros de búsqueda. El caché es *best-effort*: si Redis falla o no está disponible, el request simplemente no se cachea y sigue respondiendo con normalidad. Los resultados con `provider_status: "unavailable"` nunca se guardan en caché, para no repetir una falla temporal de Jooble.

## Observabilidad

- Cada request recibe/propaga un `X-Correlation-ID`, incluido en los logs (JSON estructurado) y en las respuestas de error.
- Los errores se devuelven como `application/problem+json` (RFC 7807): `type`, `title`, `status`, `detail`, `instance` y `correlation_id`.
- Los logs se emiten como JSON por stdout (nivel configurable con `LOG_LEVEL`).

## Pruebas

El proyecto incluye tests unitarios (`tests/`) y un conjunto de pruebas de aceptación en Gherkin con `pytest-bdd` (`tests/bdd/features/*.feature`, implementadas en `tests/bdd/test_*.py`). Jooble, PostgreSQL y Redis se sustituyen por fakes en memoria, por lo que no se necesita infraestructura externa para correrlos.

Features cubiertas:
- `job_search_and_discovery.feature` — búsqueda manual de vacantes.
- `automatic_job_recommendations.feature` — recomendaciones automáticas.
- `job_detail_view.feature` — detalle de una vacante.
- `favorite_job_management.feature` — guardar/quitar favoritos.
- `job_search_provider_resilience.feature` — circuit breaker y caché ante fallas de Jooble.

Ejecutar todo:

```powershell
pytest
```
