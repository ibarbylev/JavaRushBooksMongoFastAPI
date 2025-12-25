from fastapi import APIRouter, HTTPException, Path, Depends, Request

from app.db.models import Book, GenreEnum
from typing import List


router = APIRouter(prefix="/books")

# Dependency для получения базы данных
def get_db(request: Request):
    return request.app.state.db

# List books
@router.get("/", response_model=List[Book])
async def list_books(db=Depends(get_db)):
    books_cursor = db.books.find({})
    books = await books_cursor.to_list(length=100)
    return books


# Create book
@router.post("/", response_model=Book)
async def create_book(book: Book, db=Depends(get_db)):
    existing = await db.books.find_one({"id": book.id})
    if existing:
        raise HTTPException(status_code=400, detail="Book with this ID already exists")

    # Валидация жанров уже происходит через Enum в Pydantic
    await db.books.insert_one(book.model_dump())
    return book


# Update book
@router.put("/{book_id}", response_model=Book)
async def update_book(
    book_id: int = Path(...),
    updated_book: Book = None,
    db=Depends(get_db)
):
    existing = await db.books.find_one({"id": book_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Book not found")

    await db.books.update_one({"id": book_id}, {"$set": updated_book.model_dump()})
    updated = await db.books.find_one({"id": book_id})
    return updated


# Delete book
@router.delete("/{book_id}")
async def delete_book(book_id: int = Path(...), db=Depends(get_db)):
    existing = await db.books.find_one({"id": book_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Book not found")

    await db.books.delete_one({"id": book_id})
    return {"detail": f"Book {book_id} deleted successfully"}
