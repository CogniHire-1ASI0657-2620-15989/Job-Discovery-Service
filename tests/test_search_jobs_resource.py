import pytest
from pydantic import ValidationError

from app.interfaces.rest.resources.search_jobs_resource import SearchJobsResource


def test_search_defaults_to_ten_results_per_page():
    resource = SearchJobsResource(keywords="python", location="Lima")

    assert resource.page == 1
    assert resource.page_size == 10


def test_search_accepts_radius_from_an_http_query_string():
    resource = SearchJobsResource(keywords="python", location="Lima", radius_km="0")

    assert int(resource.radius_km) == 0


@pytest.mark.parametrize(
    ("field", "value"),
    [("page", 4), ("page_size", 21)],
)
def test_search_rejects_values_above_public_browsing_limit(field: str, value: int):
    with pytest.raises(ValidationError):
        SearchJobsResource(keywords="python", location="Lima", **{field: value})
