import pickle
import re


def save_obj(obj, name ):
    with open('obj/' + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f)


def load_obj(name ):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)


class TextFormatter:

    def __init__(self, text):
        self.text = text
        self.init_words = None
        self.separators = None

    def get_query_list(self):
        if self.text[-1] == u"\n":
            self.text = self.text[:-1]
        self.init_words = re.findall(r"(?u)\w+", self.text)
        self.separators = re.split(r"(?u)\w+", self.text)[1:]

        self.text = self.text.lower()
        query = re.findall(r"(?u)\w+", self.text)

        return query

    def format_text(self, words):
        formatted_query = ""
        if len(words) != len(self.separators):
            return " ".join(words)

        try:
            for i in range(len(words)):
                word = words[i]
                if self.init_words[i][0].isupper():
                    w = word[0].upper()
                    word = word[1:]
                    word = w + word

                formatted_query += word
                formatted_query += self.separators[i]

        except Exception:
            formatted_query = " ".join(words)

        return formatted_query
