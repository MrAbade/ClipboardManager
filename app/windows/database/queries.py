import sqlite3
import time
import datetime

class SQL_Entry():
    
    @staticmethod
    def SQL_TEXT_CREATE(cursor):
        print('Antes de criar a tabela')
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS text(
                id_text INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                element TEXT NOT NULL,
                datestamp TEXT NOT NULL
            );
        """)
        print('Depois de criar a tabela')

    @staticmethod
    def SQL_TEXT_INSERT(cursor, text):
        date = str(datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S'))
        print('tentando executar a cola do clipboard para "text"')
        print('tentando executar a query')
        cursor.execute('INSERT INTO text (id_text, element, datestamp) VALUES (NULL, ?, ?)', (text, date))
        print('saiu da query')
        return cursor.lastrowid

    @staticmethod
    def SQL_TAG_CREATE(cursor):
        print('antes de criar tabela tag')
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags(
                id_tag INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                tag TEXT NOT NULL,
                id_text INTEGER NOT NULL,
                FOREIGN KEY (id_text) REFERENCES text(id_text)
            );
        """)

    @staticmethod
    def SQL_TAG_INSERT(cursor, id_text, text_of_entry):
        tags = text_of_entry.split(',')
        for tag in tags:
            tag = tag.rstrip(' ').lstrip(' ')
            cursor.execute('INSERT INTO tags (id_tag, tag, id_text) VALUES (NULL, ?, ?)', (tag, id_text))
    
    @staticmethod
    def SQL_TEXT_EXISTS(cursor, text):
        sql = 'SELECT id_text FROM text WHERE element = ?'
        id = cursor.execute(sql, (text,))
        return id.fetchone()

class SQL_Rescue():
    
    @staticmethod
    def SQL_TEXT_QUERY(cursor, tuple_of_text_ids, tag):
        sql = 'SELECT * FROM text WHERE id_text = ?'
        tuples = []
        for id in tuple_of_text_ids:
            for row in cursor.execute(sql, (id,)):
                _row = [row[1],row[2], tag]
                tuples.append(_row)
        return tuples

    @staticmethod
    def SQL_TAG_QUERY(cursor, tag):
        sql = 'SELECT * FROM tags WHERE tag = ?'
        tuples = []
        for row in cursor.execute(sql, (tag,)):
            tuples.append(row[2])
        return tuples
