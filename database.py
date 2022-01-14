import sqlite3
from collections import defaultdict

initial_db = 'id INTEGER'
tables = {'Users': {
    'name': 'TEXT',
    'status': 'INTEGER',
    'question1': 'INTEGER',
    'question2': 'INTEGER',
    'number': 'INTEGER'
},

    'Questions': {
        'name': 'TEXT',
        'call': 'TEXT',
        'file_id': 'TEXT'
    },
    'Concepts': {
        'name': 'TEXT',
        'description': 'TEXT',
        'call': 'TEXT'
    }
}


class BotDataBase:

    def __init__(self, connect):
        self.connect = connect
        self.cursor = self.connect.cursor()
        # noinspection PyBroadException
        try:
            cursor = self.connect.cursor()
            for table in tables.keys():
                cursor.execute("CREATE TABLE IF NOT EXISTS {} ({})".format(table, initial_db))
                for k, v in tables[table].items():
                    cursor.execute("ALTER TABLE {} ADD {} {}".format(table, k, v))
            print('Таблицы были успешно созданы!')
        except sqlite3.OperationalError:
            print('Ошибка. Открыть или создать таблицыв в БД не удалось. Скорее всего, все таблицы уже созданы.')
            self.connect.commit()
        self.questions_dict = defaultdict(dict)
        self.cursor.execute('SELECT * FROM Questions')
        temp = self.cursor.fetchall()
        for answer in temp:
            self.questions_dict[answer[0]] = {'name': answer[1],
                                              'call': answer[2],
                                              'file_id': answer[3]}

        self.concepts_dict = defaultdict(dict)
        self.cursor.execute('SELECT * FROM Concepts')
        temp = self.cursor.fetchall()
        for concept in temp:
            self.concepts_dict[concept[0]] = {'name': concept[1],
                                              'description': concept[2],
                                              'call': concept[3]}

    def check_db(self, user_id):
        self.cursor.execute(f'SELECT id FROM Users WHERE id = {user_id}')
        data = self.cursor.fetchone()
        if data is None:
            return False
        else:
            return True

    def create_user(self, user_id, login):
        self.cursor.execute('INSERT INTO Users VALUES (?,?,?,?,?,?);', [user_id, login, 0, 0, 0, 0])
        self.connect.commit()


db = BotDataBase(connect=sqlite3.connect('base.db', check_same_thread=False))
