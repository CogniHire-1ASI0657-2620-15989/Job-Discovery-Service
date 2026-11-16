"""Soporte común de los tests BDD (ningún archivo de app/ se modifica).

El microservicio se prueba por su API HTTP. Jooble, PostgreSQL y Redis se
sustituyen por fakes en memoria, así que solo hacen falta los .feature para
ejecutarlo. Redis se reemplaza siempre: settings.py ejecuta load_dotenv() y un
REDIS_URL local haría que un escenario leyera resultados cacheados por otro.
Aquí viven también los steps que comparten varios features.
"""
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, then, when

from app.application.internal.command_services.default_job_search_command_service import DefaultJobSearchCommandService
from app.application.internal.query_service.default_job_search_query_service import DefaultJobSearchQueryService
from app.application.ports.job_provider import ProviderUnavailable
from app.dependencies import get_db_session, get_redis_cache
from app.domain.model.aggregates.job_offer import JobOffer
from app.interfaces.rest.controller import job_search_controller as controller
from app.main import app

USER_ID = 1
HEADERS = {"X-User-Id": str(USER_ID), "X-Internal-Api-Key": "test-key"}


def build_offer(offer_id: int) -> JobOffer:
    return JobOffer(offer_id, "jooble_pe", f"ext-{offer_id}", f"Developer {offer_id}", "ACME", "Lima",
                    "Full description and requirements", None, None, None, "https://example.test/job", None,
                    datetime.now(timezone.utc))


class FakeProvider:
    def __init__(self):
        self.down = False
        self.empty = False
        self.calls: list[dict] = []  # parámetros recibidos, para verificar qué se consultó a Jooble

    async def search(self, **params):
        self.calls.append(params)
        if self.down:
            raise ProviderUnavailable()
        if self.empty:
            return [], 0
        return [build_offer(1), build_offer(2)], 2


class FakeOfferRepo:
    def __init__(self):
        self.items: dict[int, JobOffer] = {}

    async def upsert_many(self, offers):
        for i, offer in enumerate(offers, start=1):
            offer.id = i
            self.items[i] = offer
        return offers

    async def find_by_id(self, job_offer_id):
        return self.items.get(job_offer_id)


class FakeFavoriteRepo:
    def __init__(self, offers: FakeOfferRepo):
        self.offers, self.keys = offers, set()

    async def add(self, fav):
        key = (fav.user_id, fav.job_offer_id)
        if key in self.keys:
            return False
        self.keys.add(key)
        return True

    async def remove(self, user_id, job_offer_id):
        if (user_id, job_offer_id) not in self.keys:
            return False
        self.keys.remove((user_id, job_offer_id))
        return True

    async def list_for_user(self, user_id, offset, limit):
        found = [self.offers.items[j] for (u, j) in sorted(self.keys) if u == user_id]
        return found[offset:offset + limit], len(found)


class InMemoryJsonCache:
    """Doble de RedisJsonCache con la misma interfaz async."""

    def __init__(self):
        self.store: dict[str, object] = {}

    async def get(self, key):
        return self.store.get(key)

    async def set(self, key, value, ttl_seconds):
        self.store[key] = value

    async def delete(self, key):
        self.store.pop(key, None)

    async def close(self): ...


@pytest.fixture
def world():
    offers = FakeOfferRepo()
    return SimpleNamespace(provider=FakeProvider(), offers=offers, favorites=FakeFavoriteRepo(offers),
                           cache=InMemoryJsonCache(), profile=None)


@pytest.fixture
def client(world, monkeypatch):
    for key, value in {"DATABASE_URL": "x", "JOOBLE_API_KEY": "x", "JOOBLE_BASE_URL": "http://x",
                       "GATEWAY_USER_ID_HEADER": "X-User-Id", "INTERNAL_API_KEY": "test-key"}.items():
        monkeypatch.setenv(key, value)
    from app.infrastructure.configuration.settings import get_settings
    get_settings.cache_clear()

    async def commit(): ...

    async def fake_session():
        yield None

    app.dependency_overrides[get_db_session] = fake_session
    app.dependency_overrides[get_redis_cache] = lambda: world.cache
    monkeypatch.setattr(controller, "get_job_search_command_service",
                        lambda s: DefaultJobSearchCommandService(world.provider, world.offers, world.favorites, commit))
    monkeypatch.setattr(controller, "get_job_search_query_service",
                        lambda s: DefaultJobSearchQueryService(world.offers, world.favorites))
    yield TestClient(app)
    app.dependency_overrides.clear()
    get_settings.cache_clear()


# ---------- Steps compartidos por varios features ----------
@given(parsers.parse("a job posting with ID {job_id:d} exists in the system"))
@given(parsers.parse("a job posting with ID {job_id:d} exists in the system database"))
def job_exists(world, job_id):
    world.offers.items[job_id] = build_offer(job_id)


@given("the external job search provider is available")
def provider_up(world):
    world.provider.down = False


@given("the external job search provider returns no vacancies")
def provider_empty(world):
    world.provider.empty = True


@when(parsers.parse('a {method} request is sent to "{path}"'), target_fixture="response")
def send_request(client, method, path):
    return client.request(method, path, headers=HEADERS)


@when(parsers.parse('the query parameters contain keywords "{keywords}" and location "{location}"'),
      target_fixture="response")
def search_with_params(client, keywords, location):
    return client.get("/api/v1/jobs", params={"keywords": keywords, "location": location}, headers=HEADERS)


@then(parsers.re(r"the response status is (?P<code>\d+) .+"))
def status_is(response, code):
    assert response.status_code == int(code), response.text


@then(parsers.parse('the response body contains the message "{message}"'))
def message_is(response, message):
    assert message in str(response.json().get("detail"))
