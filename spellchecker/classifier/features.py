import re


class FeatureGenerator:

    def __init__(self, lm):
        self.lm = lm
        self.__en_regex = re.compile(r'[a-z]')

    def generate_features(self, query, words):
        x = list()
        x.append(len(words))  # number of the words in the query
        x.append(len(query))  # number of the characters
        x.append(self.lm.get_prob(words))  # probability of the query
        max_prob = -1.
        min_prob = 2.

        count_of_words_in_dict = 0
        for word in words:
            prob = self.lm.get_word_prob(word)
            if prob > max_prob:
                max_prob = prob
            if prob < min_prob:
                min_prob = prob

            if word in self.lm.dict:
                count_of_words_in_dict += 1

        x.append(max_prob)  # maximum probability of the word
        x.append(min_prob)  # minimal probability of the word
        x.append(len(words) - count_of_words_in_dict)  # how many words are not in the dictionary

        if "," in query or "." in query or \
                "'" in query or ";" in query or \
                "]" in query or "[" in query or \
                "~" in query:
            x.append(1)  # bad characters in the query
        else:
            x.append(0)
        return x
