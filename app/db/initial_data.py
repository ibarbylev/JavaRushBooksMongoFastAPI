import json
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

from models import Book, GenreEnum, Author
from local_settings import MONGODB_URL_ATLAS

DB_NAME = "books_db"
BOOKS_JSON = "../../books.json"


def find_by_id(items, item_id):
    return next((item for item in items if item["id"] == item_id), None)


async def load_books():
    client = AsyncIOMotorClient(MONGODB_URL_ATLAS)
    db = client[DB_NAME]

    with open(BOOKS_JSON, encoding="utf-8") as f:
        data = json.load(f)

    if await db.books.count_documents({}) > 0:
        print("Books collection is not empty, skipping load.")
        return

    authors = data["authors"]
    genres = data["genres"]
    books = data["books"]
    details = data["book_details"]

    books_docs = []

    for book in books:
        # Author
        author_data = find_by_id(authors, book["author_id"])
        if not author_data:
            continue
        author = Author(**author_data)

        # Book details
        detail_data = next(
            (d for d in details if d["book_id"] == book["id"]),
            None
        )
        if not detail_data:
            continue

        # Genres
        book_genres = []
        for genre_id in book.get("genre_ids", []):
            genre_data = find_by_id(genres, genre_id)
            if not genre_data:
                continue
            book_genres.append(GenreEnum(genre_data["name"]))

        # Pydantic validation
        book_model = Book(
            title=book["title"],
            year_published=book["year_published"],
            is_deleted=book.get("is_deleted", False),
            summary=detail_data["summary"],
            page_count=detail_data["page_count"],
            author=author,
            genres=book_genres,
        )

        books_docs.append(book_model.model_dump())

    if books_docs:
        await db.books.insert_many(books_docs)
        print(f"Inserted {len(books_docs)} books.")


if __name__ == "__main__":
    asyncio.run(load_books())
