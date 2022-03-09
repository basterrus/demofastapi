import time
from time import sleep

import pyairtable
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey
from settings import API_KEY, USER, HOST, PASSWORD, PORT, DBNAME, BASE_ID
from sqlalchemy.orm import mapper, sessionmaker
import requests
from sqlalchemy.exc import IntegrityError


class Database:
    """ Класс - оболочка для работы с базой данных сервера."""

    class Methods:
        """Класс методы"""

        def __init__(self, name):
            self.id = None
            self.name = name

    class Psychotherapists:
        """Клас психотерапевтов"""

        def __init__(self, name, image, airtable_id):
            self.id = None
            self.name = name
            self.image = image
            self.airtable_id = airtable_id

    class Associate:
        """Класс связной таблицы"""

        def __init__(self, id_psychotherapists, id_methods):
            self.id = None
            self.id_psychotherapists = id_psychotherapists
            self.id_methods = id_methods

    def __init__(self):
        self.url = f'https://api.airtable.com/v0/{BASE_ID}/Psychotherapists?api_key={API_KEY}'
        self.table = pyairtable.Table(API_KEY, BASE_ID, 'Psychotherapists')
        self.engine = create_engine(f'postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}')
        self.metadata = MetaData()


        psychotherapists_table = Table('psychotherapists', self.metadata,
                                       Column('id', Integer, primary_key=True, autoincrement=True),
                                       Column('airtable_id', String, unique=True),
                                       Column('name', String),
                                       Column('image', String)
                                       )

        methods_table = Table('methods', self.metadata,
                              Column('id', Integer, autoincrement=True, primary_key=True),
                              Column('name', String, unique=True)
                              )

        associate_table = Table('associate', self.metadata,
                                Column('id', Integer, autoincrement=True, primary_key=True),
                                Column('id_psychotherapists', ForeignKey('psychotherapists.id')),
                                Column('id_methods', ForeignKey('methods.id'))
                                )

        self.metadata.create_all(self.engine)

        mapper(self.Methods, methods_table)
        mapper(self.Psychotherapists, psychotherapists_table)
        mapper(self.Associate, associate_table)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.session.commit()

    def get_data_from_airtable(self):
        """Функция проверяет наличие новых и удаленных записей в airtable"""

        response = requests.get(self.url).json()["records"]

        while True:
            for i in range(len(response)):
                airtable_id = response[i]["id"]
                name = response[i]["fields"]["Имя"]
                image = response[i]["fields"]["Фотография"][0]["url"]
                methods_list = response[i]["fields"]["Методы"]

                try:
                    new_doctor = self.Psychotherapists(airtable_id=airtable_id, name=name, image=image)
                    self.session.add(new_doctor)
                    self.session.commit()
                except IntegrityError:
                    self.session.rollback()

                for item in range(len(methods_list)):
                    try:
                        new_method = self.Methods(methods_list[item])
                        self.session.add(new_method)
                        self.session.commit()
                    except IntegrityError:
                        self.session.rollback()

                    try:

                        psychotherapist = self.session.query(self.Psychotherapists).filter_by(name=name).first()
                        method = self.session.query(self.Methods).filter_by(name=methods_list[item]).first()
                        id_psychotherapist = psychotherapist.id
                        id_method = method.id
                        print(id_psychotherapist, id_method)
                        associate = self.Associate(id_psychotherapists=id_psychotherapist, id_methods=id_method)
                        self.session.add(associate)
                        self.session.commit()
                    except IntegrityError:
                        self.session.rollback()
            time.sleep(60)

    def get_all_psychotherapists(self):
        query = self.session.query(self.Psychotherapists.id, self.Psychotherapists.name,
                                   self.Psychotherapists.image, self.Methods). \
            join(self.Associate, self.Associate.id_psychotherapists == self.Psychotherapists.id). \
            join(self.Methods, self.Methods.id == self.Associate.id_methods)

        return [contact for contact in query.all()]

    def get_psychotherapists_id_from_db(self, id):
        query = self.session.query(self.Psychotherapists.id, self.Psychotherapists.name,
                                   self.Psychotherapists.image, self.Methods). \
            join(self.Associate, self.Associate.id_psychotherapists == self.Psychotherapists.id). \
            join(self.Methods, self.Methods.id == self.Associate.id_methods).filter(self.Psychotherapists.id == id)

        return [contact for contact in query.all()]

    def update_psychotherapists(self, id, data):
        psychotherapists = self.session.query(self.Psychotherapists).filter_by(id=id).first()
        airtable_id = psychotherapists.airtable_id
        self.table.update(airtable_id, data)

    def add_psychotherapists(self):
        pass

    def add_method_from_db_and_airtable(self, name):
        """Функция проверяет наличие метода в базе и при отсутствии добавляет его"""

        if self.session.query(self.Methods).filter_by(name=name).count():
            print("Уже существует!")
        else:
            method = self.Methods(name)
            self.session.add(method)
            self.session.commit()

    def get_all_methods_from_db(self):
        methods = self.session.query(self.Methods).all()
        return methods

    def update_method(self, id, name):
        update_method = self.session.query(self.Methods).filter_by(id=id)
        update_method.update(name)

    def delete_method(self, id):
        try:
            method = self.session.query(self.Methods).filter_by(id=id).first()
            psychotherapists = self.session.query(self.Associate).filter_by(id_methods=method.id).first()
            count = self.session.query(self.Associate).filter_by(id_methods=method.id).count()

            if count == 0:
                print('Запись не найдена')
            else:
                for el in range(count):
                    self.session.query(self.Associate).filter(self.Associate.id_methods == method.id).delete()
                    self.session.query(self.Methods).filter(self.Methods.id == id).delete()
                    self.session.commit()
                print(f'Удалено {count} записей')

        except:
            print('Запись не найдена')


if __name__ == '__main__':
    db = Database()
    # db.get_data_from_airtable()
#     # db.get_all_psychotherapists()
#     # db.add_method_from_db_and_airtable("Психоонкология")
#     # db.add_method_from_db_and_airtable("Психоковрология")
#     # db.delete_method(1)
#     # db.update_method(1)
#     # db.get_all_psychotherapists()
#     # db.get_psychotherapists_id_from_db(1)
#     db.update_psychotherapists(1, {"name": "Иван 5"})
