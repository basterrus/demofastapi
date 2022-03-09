from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import select
from starlette.requests import Request

from database import Database

app = FastAPI()
db = Database()


class MethodNodelIn(BaseModel):
    name: str

    class Config:
        orm_mode = True


class MethodNodelOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class PsychotherapistsModelIn(BaseModel):
    id: int | None = None
    name: str
    image: str | None = None
    methods: list[int] = []

    class Config:
        orm_mode = True


class PsychotherapistsModelOut(BaseModel):
    id: int | None = None
    name: str
    image: str | None = None
    methods: list[int] = []

    class Config:
        orm_mode = True


@app.get('/psychotherapists')
async def all_psychotherapists():
    """Функция возвращает список всех доступных психотерапевтов из БД"""
    return db.get_all_psychotherapists()


@app.get('/psychotherapists/{id}')
async def get_detail_info_psychotherapist(id: int):
    """Функция возвращает детальную информацию о психотерапевте из БД"""
    return db.get_psychotherapists_id_from_db(id)


@app.post('/psychotherapists', response_model=PsychotherapistsModelOut)
async def add_psychotherapists(*, data: PsychotherapistsModelIn, request: Request):
    """Функция добавляет нового психотерапевта в БД"""

    return data


@app.patch('/psychotherapists/{id}')
async def update_psychotherapists(id: int):
    """Функция обновления информации в БД"""

    return None


@app.get('/methods')
async def get_methods_list():
    """Функция возвращает список доступных методов из БД"""
    return db.get_all_methods_from_db()


@app.post('/methods')
async def add_new_method(name: str):
    """Функция новый метод в БД"""
    db.add_method_from_db_and_airtable(name)
    return name


@app.put('/methods/{id}')
def update_method_from_db(id: int, data: MethodNodelIn):
    """Функция обновляет метод в БД"""

    update_method = db.session.query(db.Methods).filter_by(id=id).first()
    update_method.update(name=data)
    db.session.commit()
    return data


@app.delete('/methods/{id}')
async def delete_method_from_db(id: int):
    """Функция удаляет метод из БД по id"""
    db.delete_method(id)
    query = db.session.query(db.Methods).all()
    return query

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
