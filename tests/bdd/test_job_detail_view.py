from pathlib import Path

from pytest_bdd import given, parsers, scenarios, then

scenarios(str(Path(__file__).parent / "features" / "job_detail_view.feature"))


@given(parsers.parse("a job posting with ID {job_id:d} does not exist in the system"))
def job_missing(world, job_id):
    world.offers.items.pop(job_id, None)


@then("the response body contains the complete description and requirements of the job")
def full_detail(response):
    body = response.json()
    assert body["title"] and body["description_snippet"]
