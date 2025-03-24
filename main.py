from fastapi import FastAPI, HTTPException, Depends
import uvicorn
from pydantic import BaseModel, EmailStr
from typing import Annotated
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

app = FastAPI()

books = [
    {
        "id": 1,
        "title": "Асинхронность в Python",
        "author": "Меттью",
        "email": "abc@mai.ru"

    },
    {
        "id": 2,
        "title": "Backend разработка в Python",
        "author": "Артем"
    },
]

boo = []

engine = create_async_engine('sqlite+aiosqlite:///books.db')

new_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with new_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


class Base(DeclarativeBase):
    pass


class BookModel(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author: Mapped[str]


@app.post("/setup_database", summary='База книг', tags=['Библиотека'])
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    return {"ok": True}


class BookAddSchema(BaseModel):
    title: str
    author: str


class BookSchema(BookAddSchema):
    id: int


@app.post("/sql_books", summary='База книг', tags=['Библиотека'])
async def add_book(data: BookAddSchema, session: SessionDep):
    new_book = BookModel(
        title=data.title,
        author=data.author
    )
    session.add(new_book)
    await session.commit()


@app.get("/sql_books", summary='База книг', tags=['Библиотека'])
async def get_sql_book():
    pass


class BooksSchema(BaseModel):
    title: str
    author: str
    # email: EmailStr


@app.get("/books", summary='Список книг', tags=['Книги'])
def get_books():
    return books


@app.post("/boo", summary="Добавить книгу по Pydantic", tags=["Pydantis"])
def add_boo(books: BooksSchema):
    boo.append(books)
    return {"ok": True, "msg": "Книга добавлена"}


@app.get("/boo", summary="Список книг по Pydantic", tags=["Pydantis"])
def get_boo() -> list[BooksSchema]:
    return books


@app.get("/books/{book_id}", summary='Получить конкретную книгу', tags=['Книги'])
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book
        raise HTTPException(status_code=404, detail="Книга не найдена")


class NewBook(BaseModel):
    title: str
    author: str


@app.post("/books", summary='Добавить книгу', tags=['Книги'])
def create_book(new_book: NewBook):
    books.append({
        "id": len(books) + 1,
        "title": new_book.title,
        "author": new_book.author,
    })
    return {'success': True, 'message': 'Книга успешно добавлена'}


if __name__ == "__main__":
    uvicorn.run('main:app', reload=True)


data = {
    "email": "abc@mail.ru",
    "bio": None,
    "age": 12,
    "what": 234,
}


# class UserSchema(BaseModel):
#     email: EmailStr
#     bio: str | None = Field(max_length=10)
#
#     model_config = ConfigDict(extra='forbid')
#
#
# class UserAgeSchema(UserSchema):
#     age: int = Field(ge=0, le=130)
#
#
# user = UserSchema(**data)
# user1 = UserAgeSchema(**data)
#
# print(repr(user))
# print(repr(user1))
