import os
from pymongo import MongoClient

_client = None
_col = None


def _get_col():
    global _client, _col
    if _col is None:
        _client = MongoClient(os.getenv("MONGO_URL"))
        db = _client[os.getenv("MONGO_DB", "smartsearch")]
        _col = db["products"]
        _col.create_index("product_id", unique=True)
    return _col


def init_mongo():
    _get_col()  # eagerly connect & create index


def upsert_product(product: dict):
    """Insert or update a product document. Requires 'product_id' field."""
    col = _get_col()
    col.update_one(
        {"product_id": product["product_id"]},
        {"$set": product},
        upsert=True,
    )


def get_product_by_id(product_id: str) -> dict | None:
    col = _get_col()
    doc = col.find_one({"product_id": product_id}, {"_id": 0})
    return doc
