from app.domain.model.commands.search_jobs_command import SearchJobsCommand
from app.interfaces.rest.resources.search_jobs_resource import SearchJobsResource


class SearchJobsCommandFromResourceAssembler:
    @staticmethod
    def to_command(resource: SearchJobsResource) -> SearchJobsCommand:
        return SearchJobsCommand(
            keywords=resource.keywords,
            location=resource.location,
            page=resource.page,
            page_size=resource.page_size,
            radius_km=int(resource.radius_km),
        )
