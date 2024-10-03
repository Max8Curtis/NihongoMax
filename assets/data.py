import pandas as pd
import os

class MetaDataLoader:
    def __init__(self):
        self.grammar_path = r"assets//grammar"
        self.words_path = r"assets//words"
        self.kanji_path = r"assets//kanji"

        self.meta_data = {}

    def set_type(self, type):
        self.type = type

    def load_data(self, type, level):
        if type == "words":
            try:
                df = pd.read_csv(os.path.join(self.words_path, f"{str(level).lower()}.csv"), names=['exp', 'en', 'jp', 'hg', 'id'], index_col=None)
                # num_unique = pd.unique(df['exp']).shape[0]
                # return num_unique
                return df
            except Exception as e:
                print(e)
                return None
        elif type == "kanji":
            try:
                df = pd.read_csv(os.path.join(self.kanji_path, f"{str(level).lower()}.csv"), names=['exp', 'en', 'jp', 'hg', 'id'], index_col=None)
                # num_unique = pd.unique(df['exp']).shape[0]
                # return num_unique
                return df
            except Exception as e:
                print(e)
                return None
        elif type == "grammar":
            try: 
                df = pd.read_csv(os.path.join(self.grammar_path, f"{str(level).lower()}.csv"), names=['exp', 'en', 'jp', 'hg', 'id'], index_col=None)
                # num_unique = pd.unique(df['exp']).shape[0]
                # return num_unique
                return df
            except Exception as e:
                print(e)
                return None
            
    def load_meta_data(self, type, levels):
        self.meta_data[type] = {}
        for level in levels:
            df = self.load_data(type, level)
            num_unique = df['id'].max()+1 ## 'id' indexing starts at 0
            


class LevelMetaData:
    def __init__(self):
        self.metaDataLoader = MetaDataLoader()

    def get_grammar_meta_data(self, levels):
        return self.grammarMetaData.get_num_grammar(levels)
    
    def get_grammar_meta_data(self, levels):
        return self.grammarMetaData.get_num_grammar(levels)

if __name__ == "__main__":
    levelMetaData = LevelMetaData()
    print(levelMetaData.get_grammar_meta_data(levels=[f"N{str(i)}" for i in range(1,6)]))