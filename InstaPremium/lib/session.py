# Date: 05/05/2018
# Author: Mohamed
# Description: Session Handler

import json
import typing
import sqlite3
from lib.const import DB_PATH


class DatabaseWrapper:

    def __init__(self, db_name):
        self.db_name = db_name

    def db_query(self, cmd: str, args: list = [], fetchone: bool = True) -> 'result':
        '''Returns the result of an SQL command.
        '''

        database = sqlite3.connect(self.db_name)
        sql = database.cursor().execute(cmd, args)
        data = sql.fetchone()[0] if fetchone else sql.fetchall()
        database.close()
        return data

    def db_execute(self, cmd: str, args: list = []) -> None:
        '''Runs an SQL command.
        '''

        database = sqlite3.connect(self.db_name)
        database.cursor().execute(cmd, args)
        database.commit()
        database.close()


class Session(DatabaseWrapper):

    def __init__(self, fingerprint):
        super().__init__(DB_PATH)
        self.fingerprint = fingerprint
        self.create_tables()

    def create_tables(self) -> None:
        '''Creates SQL tables.
        '''

        self.db_execute('''
        CREATE TABLE IF NOT EXISTS
        Session(
            session_id TEXT,
            attempts INTEGER,
            list TEXT,
            PRIMARY KEY(session_id)
        );
        ''')

    def exists(self) -> bool:
        '''Returns True if session_id exists.
        '''

        num = self.db_query('''
        SELECT COUNT(*) 
        FROM Session
        WHERE session_id=?;
        ''', [self.fingerprint])

        return False if num == 0 else True

    def read(self) -> typing.Tuple[int, typing.List]:
        '''Returns attempts and a list of saved passwords.
        '''

        if not self.exists():
            return 0, []

        attempts, list = self.db_query('''
        SELECT attempts, list
        FROM Session
        WHERE session_id=?
        ''', args=[self.fingerprint], fetchone=False)[0]

        return attempts, json.loads(list)

    def write(self, attempts: int, passwords: list) -> None:
        '''Write to the database.
        '''

        if not self.exists():
            self.db_execute('''
            INSERT INTO Session(session_id, attempts, list)
            VALUES(?, ?, ?);
            ''', args=[self.fingerprint, attempts, json.dumps(passwords)])
            return

        self.db_execute('''
            UPDATE Session 
            SET attempts=?, list=?
            WHERE session_id=?;
            ''', args=[attempts, json.dumps(passwords), self.fingerprint])

    def delete(self) -> None:
        '''Delete a session from the database.
        '''

        if self.exists():
            self.db_execute('''
            DELETE FROM Session
            WHERE session_id=?;
            ''', args=[self.fingerprint])
