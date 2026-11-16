from pathlib import Path

from pytest_bdd import given, parsers, scenarios, then

scenarios(str(Path(__file__).parent / "features" / "job_search_and_discovery.feature"))



@then("the response body contains a paginated list of standardized job postings")
def paginated_list(response):
    body = response.json()
    assert body["provider_status"] == "available" and body["items"]
    assert {"total", "page", "page_size"} <= body.keys()


@then(parsers.parse('the response body contains an empty items list with provider status "{status}"'))
def empty_list(response, status):
    body = response.json()
    assert body["items"] == [] and body["provider_status"] == status
