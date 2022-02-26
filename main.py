from fastapi import FastAPI
from database import *


app = FastAPI()
db = Database()


@app.get('/psychotherapists')
async def get_all_psychotherapists():
    """Функция возвращает список всех доступных психотерапевтов из БД"""
    queryset = db.session.query(db.Methods)
    print(queryset)
    return queryset.all()


@app.get('/psychotherapists/{id}')
async def get_detail_info_psychotherapist(id: int):
    """Функция возвращает детальную информацию о психотерапевте из БД"""
    return None


@app.post('/psychotherapists')
async def add_psychotherapists():
    """Функция добавляет нового психотерапевта в БД"""
    return None


@app.patch('/psychotherapists/{id}')
async def update_psychotherapists(id: int):
    """Функция обновления информации в БД"""
    return None


@app.get('/methods')
async def get_methods_list():
    """Функция возвращает список доступных методов из БД"""
    return None


@app.post('/methods/{id}')
async def get_detail_info_method(id: int):
    """Функция возвращает детальную информацию о методе из БД"""
    return None


@app.put('/methods/{id}')
def update_method_from_db(id: int):
    """Функция обновляет метод в БД"""
    return None


@app.delete('/methods/{id}')
async def delete_method_from_db_and_airtable(id: int):
    """Функция удаляет метод из БД и Airtable по id"""
    return None
