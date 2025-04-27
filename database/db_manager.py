from PyQt6.QtCore import QObject
from PyQt6.QtSql import QSqlDatabase, QSqlQuery

from loggers.logger_configs import set_up_logger

logger = set_up_logger('main.database.db_manager')


class DatabaseManager(QObject):
    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path

        try:
            self.db = QSqlDatabase.addDatabase("QSQLITE")
            self.db.setDatabaseName(self.db_path)
            if not self.db.open():
                raise Exception(f"Error connecting to database: {self.db.lastError().text()}")
            else:
                self.create_table_auth()
        except Exception as e:
            print(f"Error: {str(e)}")
            logger.error(e, exc_info=True)

    def create_table_auth(self):
        create_table_query = """
            CREATE TABLE IF NOT EXISTS user_auth (
                id TEXT PRIMARY KEY,
                access_token TEXT NOT NULL,
                refresh_token TEXT NOT NULL,
                email TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                role TEXT NOT NULL,
                image_id INTEGER,
                expires_at TEXT NOT NULL,
                expires_in INTEGER NOT NULL
            );
            """
        query = QSqlQuery(self.db)
        if not query.exec(create_table_query):
            logger.error(f"Failed to create table 'user_auth': {query.lastError().text()}")

    def execute(self, query, params=None):
        q = QSqlQuery(self.db)
        if params:
            q.prepare(query)
            for i, param in enumerate(params):
                q.bindValue(i, param)
            if not q.exec():
                self.db.commit()
                print(f"Error executing query {query}: {q.lastError().text()}")
                return False
            return True
        else:
            if not q.exec(query):
                print(f"Error executing query {query}: {q.lastError().text()}")
                return False

    def check_if_row_exists(self, query, params=None):
        q = QSqlQuery(self.db)
        if params:
            q.prepare(query)
            for i, param in enumerate(params):
                q.bindValue(i, param)
            if not q.exec():
                print(f"Error executing query {query}: {q.lastError().text()}")
                return False
        else:
            if not q.exec(query):
                print(f"Error executing query {query}: {q.lastError().text()}")
                return False

        if q.next():
            exists = q.value(0)
            return exists == 1

        return False

    def execute_select(self, query, params=None):
        q = QSqlQuery(self.db)
        results = []

        if params:
            q.prepare(query)
            for i, param in enumerate(params):
                q.bindValue(i, param)
            success = q.exec()
        else:
            success = q.exec(query)

        if not success:
            print(f"Error executing SELECT query: {q.lastError().text()}")
            return None

        record = q.record()
        num_fields = record.count()
        while q.next():
            row_values = [q.value(i) for i in range(num_fields)]
            results.append(tuple(row_values))

        return results

    def table_exists(self, table_name):
        query = QSqlQuery(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
        return query.next()
