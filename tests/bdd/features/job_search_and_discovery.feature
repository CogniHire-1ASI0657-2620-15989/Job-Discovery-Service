Feature: Job Search and Discovery
    As a candidate
    I want to search for job vacancies by keywords and location
    So that I can explore opportunities outside my automatic recommendations

    Scenario: Successfully search jobs by keywords and location
        Given the external job search provider is available
        When a GET request is sent to "/api/v1/jobs"
        And the query parameters contain keywords "Python" and location "Bogota"
        Then the response status is 200 OK
        And the response body contains a paginated list of standardized job postings

    Scenario: Search returns no matches for the given term or location
        Given the external job search provider returns no vacancies
        When a GET request is sent to "/api/v1/jobs"
        And the query parameters contain keywords "Zzzz" and location "Lima"
        Then the response status is 200 OK
        And the response body contains an empty items list with provider status "available"
