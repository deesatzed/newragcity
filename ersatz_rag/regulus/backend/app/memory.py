import sqlite3

from datetime import datetime

class CaseMemory:

    def __init__(self, db_path="cases.db"):

        self.db_path = db_path

        self.init_db()

    def init_db(self):

        conn = sqlite3.connect(self.db_path)

        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS cases (

            id INTEGER PRIMARY KEY,

            timestamp TEXT,

            query TEXT,

            outcome TEXT,

            confidence_profile TEXT

        )''')

        conn.commit()

        conn.close()

    def add_case(self, query, outcome, confidence_profile):

        conn = sqlite3.connect(self.db_path)

        cursor = conn.cursor()

        cursor.execute('''INSERT INTO cases (timestamp, query, outcome, confidence_profile)

                          VALUES (?, ?, ?, ?)''',

                       (datetime.now().isoformat(), query, outcome, str(confidence_profile)))

        conn.commit()

        conn.close()

    def retrieve_cases(self, query, min_confidence):

        # Simple retrieval based on query match

        conn = sqlite3.connect(self.db_path)

        cursor = conn.cursor()

        cursor.execute('''SELECT * FROM cases WHERE query LIKE ?''', ('%' + query + '%',))

        rows = cursor.fetchall()

        conn.close()

        return rows
