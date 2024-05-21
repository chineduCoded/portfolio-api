from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


def get_db():
    """Get the database connection"""
    if settings.testing:
        from mongomock_motor import AsyncMongoMockClient
        mock_db = AsyncMongoMockClient()[settings.database_name]
        return mock_db
    else:
        client = AsyncIOMotorClient(settings.mongodb_uri)
        # client = AsyncIOMotorClient("mongodb+srv://admin:7j9nXmuOvVY4viL9@portfolio-cluster.ewd0sam.mongodb.net/mongoAPIdb?retryWrites=true&w=majority&appName=portfolio-cluster")
        return client[settings.database_name]

db = get_db()

tokens = db.get_collection("tokens")
user_collection = db.get_collection("users")
basicinfo_collection = db.get_collection("basicinfos")
skill_collection = db.get_collection("skills")
publication_collection = db.get_collection("publications")
award_collection = db.get_collection("awards")
certification_collection = db.get_collection("certifications")
interest_collection = db.get_collection("interests")
reference_collection = db.get_collection("references")
education_collection = db.get_collection("educations")
experience_collection = db.get_collection("experiences")
project_collection = db.get_collection("projects")
