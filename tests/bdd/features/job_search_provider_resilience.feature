Feature: Job Search Provider Resilience
    As a candidate
    I want the search to keep responding when the external job provider fails
    So that I am not blocked by a third-party outage

    Scenario: Search when the external provider is unavailable
        Given the external job search provider is down
        When a GET request is sent to "/api/v1/jobs"
        And the query parameters contain keywords "Java" and location "Lima"
        Then the response status is 200 OK
        And the response body indicates provider status "unavailable" with an empty items list

    Scenario: Repeated search is served from cache without calling the external provider again
        Given the external job search provider is available
        And a search for keywords "Python" and location "Lima" was already performed
        When a GET request is sent to "/api/v1/jobs"
        And the query parameters contain keywords "Python" and location "Lima"
        Then the response status is 200 OK
        And the external provider was called only once

    Scenario: Unavailable provider results are not cached
        Given the external job search provider is down
        And a search for keywords "Java" and location "Lima" was already performed
        When the external job search provider recovers
        And the query parameters contain keywords "Java" and location "Lima"
        Then the response status is 200 OK
        And the response body contains a paginated list of available job postings
