from app.domain.model.aggregates.job_offer import JobOffer
from app.interfaces.rest.resources.job_resource import JobResource


class JobResourceFromEntityAssembler:
    @staticmethod
    def to_resource(offer: JobOffer) -> JobResource:
        return JobResource(
            id=offer.id,
            provider=offer.provider,
            title=offer.title,
            company=offer.company,
            location=offer.location,
            description_snippet=offer.description_snippet,
            salary=offer.salary,
            employment_type=offer.employment_type,
            source=offer.source,
            external_url=offer.external_url,
            provider_updated_at=offer.provider_updated_at,
        )
