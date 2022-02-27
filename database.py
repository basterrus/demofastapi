from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from settings import API_KEY, USER, HOST, PASSWORD, PORT, DBNAME
from sqlalchemy.orm import mapper, sessionmaker
from datetime import datetime
import requests


class Database:
    """Модель БД"""

    class Methods:
        def __init__(self, methods):
            self.id = None
            self.methods = methods

    class Psychotherapists:
        def __init__(self, name, image, methods, airtable_id):
            self.id = None
            self.airtable_id = airtable_id
            self.name = name
            self.image = image
            self.methods = methods

    def __init__(self):
        self.url = f'https://api.airtable.com/v0/appMdHCwkJ26Mnrkz/Psychotherapists?api_key={API_KEY}'
        self.engine = create_engine(f'postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}')
        self.metadata = MetaData()

        methods_table = Table('Methods', self.metadata,
                              Column('id', Integer, primary_key=True),
                              Column('methods', String, unique=True))

        psychotherapists_table = Table('Psychotherapists', self.metadata,
                                       Column('id', Integer, primary_key=True),
                                       Column('airtable_id', String, unique=True),
                                       Column('name', String, unique=True),
                                       Column('image', String),
                                       Column('methods', ForeignKey('Methods.id'))
                                       )

        self.metadata.create_all(self.engine)

        mapper(self.Methods, methods_table)
        mapper(self.Psychotherapists, psychotherapists_table)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.session.commit()

    def get_items_airtable_and_add_to_database(self):
        response = requests.get(self.url)
        src = response.json()
        for i in range(len(src['records'])):
            airtable_id = src['records'][0]['id']
            name = src['records'][i]['fields']['Имя']
            image = src['records'][i]['fields']['Фотография'][0]['url']

            methods_pars = src['records'][i]['fields']['Методы']

            for item in range(len(methods_pars)):
                methods = methods_pars[item]
                print(methods)
                self.session.add(methods)
                self.session.commit()

            # methods = self.Methods()
            # print(methods.id)
            # new_psychotherapists = self.Psychotherapists(name, image, methods, airtable_id)
            # self.session.add(new_psychotherapists)


if __name__ == '__main__':
    db = Database()
    db.get_items_airtable_and_add_to_database()
