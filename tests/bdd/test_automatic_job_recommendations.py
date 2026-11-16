from pathlib import Path

from pytest_bdd import given, parsers, scenarios, then, when

from conftest import HEADERS

scenarios(str(Path(__file__).parent / "features" / "automatic_job_recommendations.feature"))


@given(parsers.parse('the candidate profile has expected role "{role}" and expected city "{city}"'))
def candidate_profile(world, role, city):
    world.profile = {"target_position": role, "expected_city": city}


@when("the jobs matching the candidate profile are requested", target_fixture="response")
def request_profile_jobs(client, world):
    params = {"keywords": world.profile["target_position"], "location": world.profile["expected_city"]}
    return client.get("/api/v1/jobs", params=params, headers=HEADERS)


@then(parsers.parse('the external provider was queried with keywords "{keywords}" and location "{location}"'))
def provider_queried(world, keywords, location):
    assert world.provider.calls[-1]["keywords"] == keywords
    assert world.provider.calls[-1]["location"] == location


@then("the response body contains a list of suggested job postings")
def suggested_jobs(response):
    body = response.json()
    assert body["provider_status"] == "available" and len(body["items"]) == 2


@then(parsers.parse('the response body contains an empty items list with provider status "{status}"'))
def empty_list(response, status):
    body = response.json()
    assert body["items"] == [] and body["provider_status"] == status
