import sqlite3
import pandas as pd
import numpy as np

class Database:
    def __init__(self):
        try:
            self.open()
            query = 'select sqlite_version();'
            self.cursor.execute(query)

            result = self.cursor.fetchall()
            print('SQLite Version is {}'.format(result))

        except sqlite3.Error as error:
            print('Error occurred - ', error)

    def open(self):
        self.sqliteConnection = sqlite3.connect('nihongomax.db')
        self.cursor = self.sqliteConnection.cursor()

    def close(self):
        self.cursor.close()

    def insert_levels(self):
        query = """ INSERT INTO levels(level_id, level) VALUES (1, 'N1'),(2, 'N2'),(3, 'N3'),(4, 'N4'),(5, 'N5');"""

        self.cursor.execute(query)
        self.sqliteConnection.commit()

        return self.cursor.lastrowid

    def get_table_names(self):
        query = """ SELECT 
                        name
                    FROM 
                        sqlite_schema
                    WHERE 
                        type ='table' AND 
                        name NOT LIKE 'sqlite_%';"""
        
        result = self.cursor.execute(query).fetchall()
        return result
    
    def set_user_grammar_status(self, user: int, grammar: int, state: bool):
        print(state)
        values = [user, grammar]
        if state is True:
            query = f"""INSERT OR IGNORE INTO user_grammars (user_id, grammar_id) VALUES (?,?)"""
            self.cursor.execute(query, values)
            self.sqliteConnection.commit()
        else:
            query = f"""DELETE FROM user_grammars WHERE user_id = {user} and grammar_id = {grammar};"""
            self.cursor.execute(query)
            self.sqliteConnection.commit()


    def select_random_grammar(self, user: int, level: str):
        query = f"""SELECT * FROM grammars WHERE grammar_id IN (SELECT grammar_id FROM grammars WHERE level_id = (SELECT level_id FROM levels WHERE level = '{level}')) and grammar_id NOT IN (SELECT grammar_id from user_grammars WHERE user_id = {user}) ORDER BY RANDOM() LIMIT 1;"""
        result = self.cursor.execute(query).fetchall()
        print(result)

        return result[0]

    def get_max_grammar_id(self):
        max_grammar_id_query = "SELECT grammar_id FROM grammars ORDER BY grammar_id DESC LIMIT 1;"
        max_grammar_id = self.cursor.execute(max_grammar_id_query).fetchall() # Returns list of tuple
        # print(max_grammar_id)
        if len(max_grammar_id) == 0:
            return 0

        return max_grammar_id[0][0]
    
    def get_max_example_id(self):
        max_example_id_query = "SELECT example_id FROM examples ORDER BY example_id DESC LIMIT 1;"
        max_example_id = self.cursor.execute(max_example_id_query).fetchall() # Returns list of tuple
        # print(max_example_id)
        if len(max_example_id) == 0:
            return 0
        
        return max_example_id[0][0]
    
    def clear_tables(self):
        query = "delete * from grammars;"
        self.cursor.execute(query)
        self.sqliteConnection.commit()

        query = "delete * from examples;"
        self.cursor.execute(query)
        self.sqliteConnection.commit()

    def insert_words_batch(self, file, level):
        df = pd.read_csv(file, names=["id", "jp", "ro", "hg", "types", "en"])

        query = "BEGIN TRANSACTION;" # Perform batch insert to avoid half-complete insert in case of failure
        self.cursor.execute(query)

        for i in range(df.shape[0]): # For each new word being added
            print(df["jp"].iloc[i])
            types = []
            for x in df['types'].iloc[i].split("'"): # types list is loaded as string, so convert to list
                if x != "[" and x != "]" and x != ", " and not x.upper() in types: # Check for duplicate types with different casing
                    types.append(x.upper())

            # Check that all of the words types are in the database, if not, add them
            type_ids = [] # Store the ids of all words types to use for word_types table insert
            for j in range(len(types)):
    
                

                query = f"""SELECT type_id FROM types WHERE type = '{types[j]}';"""
                result = self.cursor.execute(query).fetchall()
                # print(result)
                if result == []: # Add the new type as it does not exist in database
                    query = "SELECT max(type_id) FROM types;" # Get current highest type id
                    result = self.cursor.execute(query).fetchall()
                    if result[0][0] is None:
                        type_id = 1
                    else:
                        type_id = int(result[0][0])+1
                    values = [type_id, types[j]]
                    query = "INSERT INTO types (type_id, type) VALUES (?,?)"
                    self.cursor.execute(query, values).fetchall()
                    type_ids.append(type_id)
                else:
                    type_ids.append(int(result[0][0]))

            query = "SELECT max(word_id) FROM words;"
            result = self.cursor.execute(query).fetchall()
            if result[0][0] is None:
                word_id = 1
            else:
                word_id = result[0][0]+1 # id of new word

            query = f"""SELECT level_id FROM levels WHERE level = '{level}';"""
            result = self.cursor.execute(query).fetchall() # level id of words level
            level_id = result[0][0]

            values = [word_id, df["jp"].iloc[i], df["hg"].iloc[i], df["en"].iloc[i], level_id]
            # print(values)
            query = "INSERT INTO words (word_id, word_ka, word_hg, word_en, level_id) VALUES (?,?,?,?,?)"
            self.cursor.execute(query, values)

            for x in range(len(type_ids)):
                values = [word_id, type_ids[x]]
                print(values)
                query = "INSERT INTO word_types (word_id, type_id) VALUES (?,?)"
                self.cursor.execute(query, values)

        query = "COMMIT;"
        self.cursor.execute(query)
        self.sqliteConnection.commit()
            

    def insert_grammar(self, file, level):
        df = pd.read_csv(file, names=["grammar", "definition", "en", "jp", "hg", "url", "id"])
        grammar_points = pd.unique(df["grammar"])

        print(grammar_points)

        query = "BEGIN TRANSACTION;" # Perform batch insert to avoid half-complete insert in case of failure
        self.cursor.execute(query)
        

        for i in range(grammar_points.shape[0]):
            examples = df[df["grammar"] == grammar_points[i]]
            # index = np.where(df['grammar'] == grammar_points[i])[0]
            grammar_point = examples.iloc[0]

            query = f"""SELECT level_id FROM levels WHERE level = '{level}';"""
            level_id = self.cursor.execute(query).fetchall()[0][0]
            grammar_id = self.get_max_grammar_id() + 1
            values = [grammar_id, grammar_point["definition"], grammar_point["grammar"], grammar_point["url"], level_id]
            print(values)
            query = """INSERT INTO grammars (grammar_id, grammar_en, grammar_jp, image_url, level_id) VALUES (?,?,?,?,?);"""

            self.cursor.execute(query, values)
            # self.sqliteConnection.commit()

                       
            # examples = df[df["grammar"] == grammar_point["grammar"]] # Get all examples for current grammar point

            for j in range(examples.shape[0]):
                example_id = self.get_max_example_id() + 1
                values = [example_id, examples["jp"].iloc[j], examples["hg"].iloc[j], examples["en"].iloc[j], grammar_id]
                # print(values)

                query = "INSERT INTO examples (example_id, example_jp, example_hg, example_en, grammar_id) VALUES (?,?,?,?,?);"

                self.cursor.execute(query, values)
                # self.sqliteConnection.commit()

        query = "COMMIT;"
        self.cursor.execute(query)
        self.sqliteConnection.commit()

    def createTables(self):
        levels_table = """ CREATE TABLE IF NOT EXISTS levels (
            level_id INTEGER NOT NULL,
            level VARCHAR(3) NOT NULL,
            PRIMARY KEY(level_id)
        ) WITHOUT ROWID;""" 

        words_table = """ CREATE TABLE IF NOT EXISTS words (
            word_id INTEGER NOT NULL,
            word_ka CHAR(25) NOT NULL,
            word_hg CHAR(25) NOT NULL,
            word_en CHAR(100) NOT NULL,
            level_id INTEGER NOT NULL,
            PRIMARY KEY (word_id),
            FOREIGN KEY (level_id) REFERENCES levels(level_id)
            ) WITHOUT ROWID; """
        
        types_table = """ CREATE TABLE IF NOT EXISTS types (
            type_id INTEGER NOT NULL,
            type CHAR(25) NOT NULL,
            PRIMARY KEY (type_id)
        ) WITHOUT ROWID;"""

        words_types_table = """ CREATE TABLE IF NOT EXISTS word_types (
            word_id INTEGER NOT NULL,
            type_id INTEGER NOT NULL,
            FOREIGN KEY (word_id) REFERENCES words(word_id),
            FOREIGN KEY (type_id) REFERENCES types(type_id),
            PRIMARY KEY(word_id, type_id)
            ) WITHOUT ROWID;"""

        grammars_table = """ CREATE TABLE IF NOT EXISTS grammars (
            grammar_id INTEGER NOT NULL,
            grammar_en VARCHAR(50) NOT NULL,
            grammar_jp VARCHAR(50) NOT NULL,
            image_url VARCHAR(500) NOT NULL,
            level_id INTEGER NOT NULL,
            PRIMARY KEY (grammar_id),
            FOREIGN KEY (level_id) REFERENCES levels(level_id)
        ) WITHOUT ROWID;"""

        examples_table = """ CREATE TABLE IF NOT EXISTS examples (
            example_id INTEGER NOT NULL,
            example_jp VARCHAR(150) NOT NULL,
            example_hg VARCHAR(150) NOT NULL,
            example_en VARCHAR(150) NOT NULL,
            grammar_id INTEGER NOT NULL,
            PRIMARY KEY(example_id),
            FOREIGN KEY (grammar_id) REFERENCES grammar(grammar_id)
        ) WITHOUT ROWID;"""

        kanji_table = """ CREATE TABLE IF NOT EXISTS kanjis (
            kanji_id INTEGER NOT NULL,
            kanji VARCHAR(10) NOT NULL,
            onyomi VARCHAR(10) NOT NULL,
            kunyomi VARCHAR(10),
            meaning VARCHAR(150) NOT NULL,
            image_url VARCHAR(500) NOT NULL,
            level_id INTEGER NOT NULL,
            PRIMARY KEY (kanji_id),
            FOREIGN KEY (level_id) REFERENCES levels(level_id)
        ) WITHOUT ROWID;"""

        users_table = """ CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER NOT NULL,
            date_joined TEXT NOT NULL,
            PRIMARY KEY (user_id)
        );"""

        user_grammars_table = """ CREATE TABLE IF NOT EXISTS user_grammars (
            user_id INTEGER NOT NULL,
            grammar_id INTEGER NOT NULL,
            PRIMARY KEY (user_id, grammar_id),
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (grammar_id) REFERENCES grammars (grammar_id)
        );"""

        user_words_table = """ CREATE TABLE IF NOT EXISTS user_words (
            user_id INTEGER NOT NULL,
            word_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (word_id) REFERENCES words (word_id)
        );"""

        user_kanjis_table = """ CREATE TABLE IF NOT EXISTS user_kanjis (
            user_id INTEGER NOT NULL,
            kanji_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (kanji_id) REFERENCES kanjis (kanji_id)
        );"""

        self.cursor.execute(levels_table)
        self.cursor.execute(words_table)
        self.cursor.execute(types_table)
        self.cursor.execute(words_types_table)
        self.cursor.execute(grammars_table)
        self.cursor.execute(examples_table)
        self.cursor.execute(kanji_table)
        self.cursor.execute(users_table)
        self.cursor.execute(user_grammars_table)
        self.cursor.execute(user_words_table)
        self.cursor.execute(user_kanjis_table)


        result = self.cursor.fetchall()
        print(result)
        
    def drop_tables(self):
        query = "DROP TABLE IF EXISTS examples"
        self.cursor.execute(query)
        self.sqliteConnection.commit()

        query = "DROP TABLE IF EXISTS grammars"
        self.cursor.execute(query)
        self.sqliteConnection.commit()

        query = "DROP TABLE IF EXISTS kanjis"
        self.cursor.execute(query)
        self.sqliteConnection.commit()

        query = "DROP TABLE IF EXISTS word_types"
        self.cursor.execute(query)
        self.sqliteConnection.commit()

        query = "DROP TABLE IF EXISTS words"
        self.cursor.execute(query)
        self.sqliteConnection.commit()

        query = "DROP TABLE IF EXISTS types"
        self.cursor.execute(query)
        self.sqliteConnection.commit()

        query = "DROP TABLE IF EXISTS levels"
        self.cursor.execute(query)
        self.sqliteConnection.commit()

        query = "DROP TABLE IF EXISTS users"
        self.cursor.execute(query)
        self.sqliteConnection.commit()

        query = "DROP TABLE IF EXISTS user_grammars"
        self.cursor.execute(query)
        self.sqliteConnection.commit()

        query = "DROP TABLE IF EXISTS user_words"
        self.cursor.execute(query)
        self.sqliteConnection.commit()

        query = "DROP TABLE IF EXISTS user_kanjis"
        self.cursor.execute(query)
        self.sqliteConnection.commit()

    def add_user_grammar(self, grammar: int, user: int):
        query = f"INSERT INTO user_grammars (user_id, grammar_id) VALUES ({user}, {grammar});"

        self.cursor.execute(query)
        self.sqliteConnection.commit()

        return True
    
    def get_grammar_info(self, id: int):
        query = f"""SELECT image_url FROM grammars WHERE grammar_id = {id};"""

        result = self.cursor.execute(query).fetchall()
        if not result[0][0] is None:
            return result[0][0]
        else:
            return None

    def get_grammars(self, level: str, user: int):
        query = f"SELECT * FROM grammars WHERE grammar_id IN (SELECT grammar_id FROM user_grammars WHERE user_id = {user})"

        df = pd.read_sql_query(query, self.sqliteConnection)
        return df

    def get_grammars(self, level: str):
        query = f"SELECT * FROM grammars WHERE level_id IN (SELECT level_id FROM levels WHERE level = '{level.upper()}')"

        df = pd.read_sql_query(query, self.sqliteConnection)
        return df

    def get_examples(self, grammar_id: int):
        query = f"SELECT * FROM examples WHERE grammar_id = {grammar_id}"

        df = pd.read_sql_query(query, self.sqliteConnection)
        return df
    
    def get_num_grammars_at_level(self, level: str):
        try:
            query = f"SELECT count(*) FROM grammars WHERE level_id IN (SELECT level_id FROM levels WHERE level = '{level}');"

            result = self.cursor.execute(query).fetchall()[0][0]
            return result
        except Exception as e:
            return None
    
    def get_num_kanjis_at_level(self, level: str):
        try:
            query = f"SELECT count(*) FROM kanjis WHERE level_id IN (SELECT level_id FROM levels WHERE level = '{level}');"

            result = self.cursor.execute(query).fetchall()[0][0]
            return result
        except Exception as e:
            return None
    
    def get_num_words_at_level(self, level: str):
        try:
            query = f"SELECT count(*) FROM words WHERE level_id IN (SELECT level_id FROM levels WHERE level = '{level}');"

            result = self.cursor.execute(query).fetchall()[0][0]
            return result
        except Exception as e:
            return None
        
    def get_num_grammars_at_level_user(self, level: str, user: int):
        try:
            query = f"SELECT count(*) FROM user_grammars WHERE user_id = {user} AND grammar_id IN (SELECT grammar_id FROM grammars WHERE level = {level});"
            result = self.cursor.execute(query).fetchall()[0][0]
            return result
        except Exception as e:
            return None
        
    def get_num_words_at_level_user(self, level: str, user: int):
        try:
            query = f"SELECT count(*) FROM user_words WHERE user_id = {user} AND word_id IN (SELECT word_id FROM words WHERE level = {level});"
            result = self.cursor.execute(query).fetchall()[0][0]
            return result
        except Exception as e:
            return None
        
    def get_num_kanjis_at_level_user(self, level: str, user: int):
        try:
            query = f"SELECT count(*) FROM user_kanjis WHERE user_id = {user} AND kanji_id IN (SELECT kanji_id FROM kanjis WHERE level = {level});"
            result = self.cursor.execute(query).fetchall()[0][0]
            return result
        except Exception as e:
            return None



if __name__ == "__main__":
    db = Database()
    
    # db.drop_tables()
    db.createTables()
    # db.insert_levels()
    # db.createTables()
    # print()
    # db.insert_grammar("assets//grammar//n1.csv", "N1")
    # db.insert_words_batch("assets//words//n2.csv", "N2")
    # db.get_grammars("n1")
    db.get_num_grammars_at_level('N2')
    db.close()
