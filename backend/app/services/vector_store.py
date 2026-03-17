from app.db.mongo_service import db

collection = db["paper_vectors"]


async def store_document_embedding(doc):

    await collection.insert_one(doc)