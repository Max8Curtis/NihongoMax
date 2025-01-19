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

            self.grammar_schema = {"grammar_id": None, "grammar_en": None, "grammar_jp": None, "image_url": None, "level_id": None}

        except sqlite3.Error as error:
            print('Error occurred - ', error)

    def open(self):
        self.sqliteConnection = sqlite3.connect('nihongomax.db')
        self.cursor = self.sqliteConnection.cursor()

    def close(self):
        self.cursor.close()

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

        texts_table = """ CREATE TABLE IF NOT EXISTS texts (
            text_id INTEGER NOT NULL,
            title VARCHAR(150) NOT NULL,
            author VARCHAR(50),
            PRIMARY KEY (text_id)
        ) WITHOUT ROWID;"""

        text_types_table = """ CREATE TABLE IF NOT EXISTS texts_types (
            type_id INTEGER NOT NULL,
            type VARCHAR(50) NOT NULL,
            PRIMARY KEY (type_id)
        ) WITHOUT ROWID;"""

        text_types_link_table = """ CREATE TABLE IF NOT EXISTS texts_types_link (
            text_id INTEGER NOT NULL,
            type_id INTEGER NOT NULL,
            PRIMARY KEY(text_id, type_id),
            FOREIGN KEY (text_id) REFERENCES texts (text_id),
            FOREIGN KEY (type_id) REFERENCES texts_types (type_id)
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
            FOREIGN KEY (grammar_id) REFERENCES grammars (grammar_id),
            UNIQUE(user_id, grammar_id)
        );"""

        user_words_table = """ CREATE TABLE IF NOT EXISTS user_words (
            user_id INTEGER NOT NULL,
            word_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (word_id) REFERENCES words (word_id),
            UNIQUE(user_id, word_id)
        );"""

        user_kanjis_table = """ CREATE TABLE IF NOT EXISTS user_kanjis (
            user_id INTEGER NOT NULL,
            kanji_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (kanji_id) REFERENCES kanjis (kanji_id),
            UNIQUE(user_id, kanji_id)
        );"""

        self.cursor.execute(levels_table)
        self.cursor.execute(words_table)
        self.cursor.execute(types_table)
        self.cursor.execute(words_types_table)
        self.cursor.execute(grammars_table)
        self.cursor.execute(examples_table)
        self.cursor.execute(kanji_table)
        self.cursor.execute(texts_table)
        self.cursor.execute(text_types_table)
        self.cursor.execute(text_types_link_table)
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

    def insert_levels(self):
        query = """ INSERT INTO levels(level_id, level) VALUES (1, 'N1'),(2, 'N2'),(3, 'N3'),(4, 'N4'),(5, 'N5');"""

        self.cursor.execute(query)
        self.sqliteConnection.commit()

        return self.cursor.lastrowid
    
    def insert_text_types(self):
        query = """ INSERT INTO texts_types(type_id, type) VALUES (1, 'hiragana'), (2, 'katakana'); """

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
    
    def get_next_grammar(self, user: int, level: str, grammar: int):
        if grammar is None:
            query = f"""SELECT * FROM grammars WHERE grammar_id IN (SELECT grammar_id FROM grammars WHERE level_id = (SELECT level_id FROM levels WHERE level = '{level}')) and grammar_id NOT IN (SELECT grammar_id from user_grammars WHERE user_id = {user}) ORDER BY grammar_id ASC LIMIT 1;"""
            result = self.cursor.execute(query).fetchall()
            if result == []: # No remaining grammar points to study
                    return None
        else:
            query = f"""SELECT * FROM grammars WHERE grammar_id IN (SELECT grammar_id FROM grammars WHERE level_id = (SELECT level_id FROM levels WHERE level = '{level}')) and grammar_id NOT IN (SELECT grammar_id from user_grammars WHERE user_id = {user}) and grammar_id > {grammar} ORDER BY grammar_id ASC LIMIT 1;"""
            result = self.cursor.execute(query).fetchall()
            if result == []: # No remaining grammar points with higher ids than the current grammar
                # Check grammar points with lower ids
                query = f"""SELECT * FROM grammars WHERE grammar_id IN (SELECT grammar_id FROM grammars WHERE level_id = (SELECT level_id FROM levels WHERE level = '{level}')) and grammar_id NOT IN (SELECT grammar_id from user_grammars WHERE user_id = {user}) and grammar_id < {grammar} ORDER BY grammar_id ASC LIMIT 1;"""
                result = self.cursor.execute(query).fetchall()
                if result == []: # No remaining grammar points to study
                    return None

        return result[0]

    def set_user_grammar_status(self, user: int, grammar: int, state: bool):

        values = [int(user), int(grammar)]
        print(values)
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

        return result[0]
    
    def get_max_text_id(self):
        max_text_id_query = "SELECT text_id FROM texts ORDER BY text_id DESC LIMIT 1;"
        max_text_id = self.cursor.execute(max_text_id_query).fetchall() # Returns list of tuple
        print(f'Max text: {max_text_id}')
        if len(max_text_id) == 0:
            return 0
        
        return max_text_id[0][0]

    def get_max_grammar_id(self):
        max_grammar_id_query = "SELECT grammar_id FROM grammars ORDER BY grammar_id DESC LIMIT 1;"
        max_grammar_id = self.cursor.execute(max_grammar_id_query).fetchall() # Returns list of tuple
        print(f'Max grammar: {max_grammar_id}')
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

    def get_level(self, level):
        query = f"""SELECT level_id FROM levels WHERE level = '{level}';"""
        level_id = self.cursor.execute(query).fetchall()[0][0]

        return level_id

    def insert_words_batch(self, file, level):
        df = pd.read_csv(file, names=['id', 'ka', 'hg', 'ro', 'types', 'en'])

        query = "BEGIN TRANSACTION;" # Perform batch insert to avoid half-complete insert in case of failure
        self.cursor.execute(query)

        for i in range(df.shape[0]): # For each new word being added
            print(df["ka"].iloc[i])
            # Check if word is already in the database
            query = f"SELECT * FROM words WHERE words.word_ka = '{df['ka'].iloc[i]}';"
            result = self.cursor.execute(query).fetchall()
            print(result)
            if result != []:
                print(f"word {df['ka'].iloc[i]} already exists")
                continue
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

            level_id = self.get_level(level)

            values = [word_id, df["ka"].iloc[i], df["hg"].iloc[i], df["en"].iloc[i], level_id]

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
            

    def insert_grammar_batch(self, file, level):
        df = pd.read_csv(file, names=["grammar", "definition", "en", "jp", "hg", "url", "id"])
        grammar_points = pd.unique(df["grammar"])

        # print(grammar_points)

        query = "BEGIN TRANSACTION;" # Perform batch insert to avoid half-complete insert in case of failure
        self.cursor.execute(query)
        grammar_id = self.get_max_grammar_id()

        for i in range(grammar_points.shape[0]):
            examples = df[df["grammar"] == grammar_points[i]]
            # index = np.where(df['grammar'] == grammar_points[i])[0]
            grammar_point = examples.iloc[0]
            grammar_id += 1
            # print(grammar_id)

            level_id = self.get_level(level)
            
            values = [grammar_id, grammar_point["definition"], grammar_point["grammar"], grammar_point["url"], level_id]
            # print(values)
            query = """INSERT INTO grammars (grammar_id, grammar_en, grammar_jp, image_url, level_id) VALUES (?,?,?,?,?);"""

            self.cursor.execute(query, values)
            
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

    def insert_texts_batch(self, texts):
        query = "BEGIN TRANSACTION;" # Perform batch insert to avoid half-complete insert in case of failure
        self.cursor.execute(query)
        text_id = self.get_max_text_id()
        new_id = int(text_id)

        for t in range(len(texts)):
            fields = texts[t].split('#')
            types = fields[2]
            if ',' in types:
                types = types.split(',')
            else:
                types = [types]

            type_string = ""
            for i in types:
                type_string += "'" + i + "',"
            type_string = type_string[:len(type_string)-1]

            query = f""" SELECT type_id FROM texts_types WHERE type IN ({type_string}); """
            result = self.cursor.execute(query).fetchall()
            if result == []:
                continue
            else:
                # print(result)
                type_ids = [result[i][0] for i in range(len(result))]
                new_id += 1

            title = fields[0]
            author = fields[1]

            texts_types_string = ""
            for i in type_ids:
                texts_types_string += f"({new_id}, {i}),"
            texts_types_string = texts_types_string[:len(texts_types_string)-1]

            print(type_ids)
            query = f""" INSERT INTO texts_types_link (text_id, type_id) VALUES {texts_types_string}; """
            print(query)
            self.cursor.execute(query)

            values = [new_id, title, author]
            query = f""" INSERT INTO texts (text_id, title, author) VALUES (?,?,?); """

            self.cursor.execute(query, values)

        query = "COMMIT;"
        self.cursor.execute(query)
        self.sqliteConnection.commit()

    def add_user_grammar(self, grammar: int, user: int):
        query = f"INSERT INTO user_grammars (user_id, grammar_id) VALUES ({user}, {grammar});"

        self.cursor.execute(query)
        self.sqliteConnection.commit()

        return True
    
    def add_user_words(self, words: list[int], user: int):
        query = "BEGIN TRANSACTION;" # Perform batch insert to avoid half-complete insert in case of failure
        self.cursor.execute(query)

        query = "INSERT INTO user_words (user_id, word_id) VALUES "
        for i in range(len(words)):
            query += f"({user}, {words[i]}),"

        query = query[:len(query)-1] + ";"
        print(query)
        self.cursor.execute(query)

        query = "COMMIT;"
        self.cursor.execute(query)
        self.sqliteConnection.commit()

    
    def get_grammar_info(self, id: int):
        query = f"""SELECT * FROM grammars WHERE grammar_id = {id};"""

        result = self.cursor.execute(query).fetchall()
        if not result[0][0] is None:
            grammar = self.grammar_schema
            grammar["grammar_id"], grammar["grammar_en"], grammar["grammar_jp"], grammar["image_url"], grammar["level_id"] = result[0][0],result[0][1],result[0][2],result[0][3],result[0][4]
            return grammar
        else:
            return None

    def get_user_grammars_all(self, level:str, user:int):
        level_grammars = self.get_grammars(level)
        user_grammars = self.get_user_grammars_completed(level, user)
        level_grammars['completed'] = level_grammars['grammar_id'].isin(user_grammars['grammar_id']) # Add new column indicating if each grammar point has been completed by user

        return level_grammars

    def get_user_grammars_completed(self, level: str, user: int):
        query = f"SELECT * FROM grammars WHERE grammar_id IN (SELECT grammar_id FROM user_grammars WHERE user_id = {user})"

        df = pd.read_sql_query(query, self.sqliteConnection)
        return df
    
    def get_user_grammars_not_completed(self, level: str, user: int):
        query = f"""SELECT * FROM grammars WHERE level_id IN (SELECT level_id FROM levels WHERE level = '{level.upper()}') AND grammar_id NOT IN (SELECT grammar_id FROM user_grammars WHERE user_id = {user});"""
        
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
    
    def get_words_at_level(self, level: str):
        try:
            query = f"SELECT * FROM words WHERE level_id IN (SELECT level_id FROM levels WHERE level = '{level}');"
            result = self.cursor.execute(query).fetchall()
            return result
        except Exception as e:
            return None
    
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
        # try:
        query = f"SELECT count(*) FROM user_grammars WHERE user_id = {user} AND grammar_id IN (SELECT grammar_id FROM grammars WHERE level_id IN (SELECT level_id FROM levels WHERE level = '{level}'));"
        result = self.cursor.execute(query).fetchall()[0][0]
        return result
        # except Exception as e:
        #     return None
        
    def get_num_words_at_level_user(self, level: str, user: int):
        try:
            query = f"SELECT count(*) FROM user_words WHERE user_id = {user} AND word_id IN (select word_id FROM words WHERE level_id IN (select level_id FROM levels WHERE level = '{level}'));"
            result = self.cursor.execute(query).fetchall()[0][0]
            return result
        except Exception as e:
            return None
        
    def get_num_kanjis_at_level_user(self, level: str, user: int):
        try:
            query = f"SELECT count(*) FROM user_kanjis WHERE user_id = {user} AND kanji_id IN (select kanji_id FROM kanjis WHERE level_id IN (select level_id FROM levels WHERE level = '{level}'));"
            result = self.cursor.execute(query).fetchall()[0][0]
            return result
        except Exception as e:
            return None
        
    def get_words_at_level_user(self, level: str, user: int):
        # get the words, along with their types, that user has studied in level
        # try:
        query = f"SELECT w.word_id, w.word_ka, w.word_hg, w.word_en, w.level_id, wt.type_id, t.type FROM words AS w INNER JOIN word_types AS wt ON w.word_id = wt.word_id INNER JOIN types AS t ON wt.type_id = t.type_id WHERE w.word_id IN (SELECT word_id FROM user_words WHERE user_id = {user}) and level_id IN (SELECT level_id FROM levels WHERE level = '{level}');"
        
        df = pd.read_sql_query(query, self.sqliteConnection)
        return df
        # except Exception as e:
            # return None

    def get_text_types(self):
        try:
            query = f""" SELECT * FROM texts_types; """
            df = pd.read_sql_query(query, self.sqliteConnection)
            return df
        except Exception as e:
            return None


    def get_texts_all(self):
        try:
            query = f""" SELECT t.text_id, t.title, t.author, tt.type_id FROM texts AS t JOIN texts_types_link AS tt ON t.text_id = tt.text_id; """

            df = pd.read_sql_query(query, self.sqliteConnection)
            type_ids = df.groupby('text_id')
            df_new = df.iloc[[type_ids.groups[i][0] for i in list(type_ids.groups.keys())]]
            df_new['type_id'] = list(type_ids.agg({'type_id': lambda x: list(x)})['type_id'])
            return df_new
        except Exception as e:
            return None


import itertools #######################################
if __name__ == "__main__":
    db = Database()

    db.createTables()
    
    level = 'N1'
    user = 1

    # db.insert_text_types()

    # texts = ['Test1#Test1#hiragana,katakana']
    # db.insert_texts_batch(texts)
    types = db.get_text_types()
    print(types)
    stuff = [(types['type_id'].iloc[x], types['type'].iloc[x]) for x in range(types.shape[0])]
    # stuff = [1, 2, 3]
    for L in range(len(stuff) + 1):
        for subset in itertools.combinations(stuff, L):
            print(subset)
    
    db.close()
