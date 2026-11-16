Feature: Job Detail View
    As a candidate
    I want to select a job offering to read the full description and required qualifications
    So that I can decide if it interests me

    Scenario: Successfully retrieve job details by ID
        Given a job posting with ID 4821 exists in the system database
        When a GET request is sent to "/api/v1/jobs/4821"
        Then the response status is 200 OK
        And the response body contains the complete description and requirements of the job

    Scenario: Attempt to retrieve a job posting that no longer exists
        Given a job posting with ID 9999 does not exist in the system
        When a GET request is sent to "/api/v1/jobs/9999"
        Then the response status is 404 Not Found
        And the response body contains the message "Job offer not found."