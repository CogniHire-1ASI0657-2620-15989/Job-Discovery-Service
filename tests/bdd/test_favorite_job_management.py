from pathlib import Path

from pytest_bdd import given, parsers, scenarios, then

from conftest import USER_ID, build_offer

scenarios(str(Path(__file__).parent / "features" / "favorite_job_management.feature"))


@given(parsers.parse("the job posting with ID {job_id:d} is already marked as favorite by the candidate"))
def already_favorite(world, job_id):
    world.offers.items[job_id] = build_offer(job_id)
    world.favorites.keys.add((USER_ID, job_id))


@given("the candidate has saved multiple job postings as favorites")
def several_favorites(world):
    for job_id in (10, 11, 12):
        world.offers.items[job_id] = build_offer(job_id)
        world.favorites.keys.add((USER_ID, job_id))


@then("the response body confirms the favorite was created with created status true")
def favorite_created(response):
    assert response.json()["created"] is True


@then("the response body contains a paginated list of the candidate's favorite jobs")
def favorites_list(response):
    body = response.json()
    assert len(body["items"]) == 3 and body["total"] == 3 and body["page"] == 1
