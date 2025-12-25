from pydantic import BaseModel
from enum import Enum


class GenreEnum(str, Enum):
    """Book Genres"""
    Classic = "Classic"
    Fiction = "Fiction"
    Satire = "Satire"
    Romance = "Romance"
    Dystopian = "Dystopian"


class Author(BaseModel):
    """Authors"""
    id: int
    name: str


class Book(BaseModel):
    """Book and Book Details"""
    id: int
    title: str
    year_published: int
    is_deleted: bool = False
    summary: str
    page_count: int

    author: Author  # instead object Author
    genres: list[GenreEnum]  # List Enum objects
