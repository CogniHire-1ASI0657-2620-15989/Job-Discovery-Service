Feature: Favorite Job Management
    As a candidate
    I want to mark job vacancies as favorites
    So that I don't lose track of them and can analyze them later

    Scenario: Successfully add a job posting to favorites
        Given a job posting with ID 4821 exists in the system
        When a POST request is sent to "/api/v1/jobs/4821/favorite"
        Then the response status is 200 OK
        And the response body confirms the favorite was created with created status true

    Scenario: Successfully remove a job posting from favorites
        Given the job posting with ID 4821 is already marked as favorite by the candidate
        When a DELETE request is sent to "/api/v1/jobs/4821/favorite"
        Then the response status is 204 No Content

    Scenario: Successfully list all saved favorite jobs
        Given the candidate has saved multiple job postings as favorites
        When a GET request is sent to "/api/v1/favorites"
        Then the response status is 200 OK
        And the response body contains a paginated list of the candidate's favorite jobs