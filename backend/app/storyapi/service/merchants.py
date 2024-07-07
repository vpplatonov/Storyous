from storyapi.db.merchants import Merchant
from storyapi.service.auth import ABCStoryService


class MerchantsAPI(ABCStoryService[Merchant]):
    endpoint = "/merchants"
