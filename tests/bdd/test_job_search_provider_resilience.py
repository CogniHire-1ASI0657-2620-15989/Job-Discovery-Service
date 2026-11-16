from pathlib import Path

from pytest_bdd import given, parsers, scenarios, then, when

from conftest import HEADERS

scenarios(str(Path(__file__).parent / "features" / "job_search_provider_resilience.feature"))


@given("the external job search provider is down")
def provider_down(world):
    world.provider.down = True


@then('the response body indicates provider status "unavailable" with an empty items list')
def provider_unavailable(response):
    body = response.json()
    assert body["provider_status"] == "unavailable" and body["items"] == []



@given(parsers.parse('a search for keywords "{keywords}" and location "{location}" was already performed'))
def previous_search(client, keywords, location):
    client.get("/api/v1/jobs", params={"keywords": keywords, "location": location}, headers=HEADERS)


@when("the external job search provider recovers")
def provider_recovers(world):
    world.provider.down = False


@then("the external provider was called only once")
def provider_called_once(world):
    assert len(world.provider.calls) == 1


@then("the response body contains a paginated list of available job postings")
def available_postings(response):
    body = response.json()
    assert body["provider_status"] == "available" and body["items"]
