from storyapi.db import source_set, SourceId
from storyapi.db.bills import Bills, BillsList
from storyapi.service.auth import ABCStoryService


class BillsAPI(ABCStoryService[Bills]):
    endpoint = "/bills"

    def get_url(self, source: SourceId, bill_id: str) -> str:
        source_id = source.get_source_id()
        return super().get_url(source_id, bill_id)


class BillsListAPI(ABCStoryService[BillsList]):
    endpoint = "/bills"

    def get_url(self, source: SourceId) -> str:
        source_id = source.get_source_id()
        source_dump = source.model_dump(exclude=source_set, by_alias=True, exclude_none=True)
        return super().get_url(source_id, **source_dump)
