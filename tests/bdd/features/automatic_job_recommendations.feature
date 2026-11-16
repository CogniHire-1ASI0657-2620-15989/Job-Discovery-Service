Feature: Automatic Job Recommendations
    As a candidate
    I want to see suggested job offers as soon as I open the application
    So that I can save time searching for opportunities

    # US07. Job Discovery no expone un endpoint dedicado de recomendaciones: el Home
    # consulta "/api/v1/jobs" usando el cargo y la ciudad esperados del perfil (Identity).

    Scenario: Retrieve suggested jobs using the expected role and city of a complete profile
        Given the candidate profile has expected role "Backend Developer" and expected city "Lima"
        When the jobs matching the candidate profile are requested
        Then the response status is 200 OK
        And the external provider was queried with keywords "Backend Developer" and location "Lima"
        And the response body contains a list of suggested job postings

    Scenario: No suggestions when the external providers return no results for the profile
        Given the candidate profile has expected role "Backend Developer" and expected city "Lima"
        And the external job search provider returns no vacancies
        When the jobs matching the candidate profile are requested
        Then the response status is 200 OK
        And the response body contains an empty items list with provider status "available"
