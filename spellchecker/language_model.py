import re


class LanguageModel:

    def __init__(self, filename):
        # {"word" : {"freq" : frequency_of_word, "word" : {"next_words" : frequency_of_pair}}}
        self.dict = dict()
        # the counter of all words in all lines
        self.size = 0
        self.default_frequency = 0
        self.WORDS = re.compile(r"(?u)\w+")
        self.fit(filename)

    def fit(self, filename):
        with open(filename) as f:
            lines = f.readlines()
        num_line = 0
        for line in lines:
            num_line += 1
            print(f"\r{num_line} lines are processed...", end='', flush=True)
            line = line.lower()
            line = line[:-1]
            index = line.find('\t')
            # we consider only right queries
            if index > 0:
                line = line[index + 1:]

            words = self.WORDS.findall(line)
            for i in range(len(words)):
                word = words[i]
                if word in self.dict:
                    self.dict[word]["freq"] += 1
                else:
                    self.dict[word] = {"freq": 1,
                                       "words": {}}
                self.size += 1

                if i != len(words) - 1:
                    if words[i + 1] in self.dict[word]["words"]:
                        self.dict[word]["words"][words[i + 1]] += 1
                    else:
                        self.dict[word]["words"][words[i + 1]] = 1

        for value in self.dict.values():
            value["freq"] /= self.size
            pairs_count = sum(value["words"].values())
            for word in value["words"]:
                value["words"][word] /= pairs_count
        self.default_frequency = 1 / self.size
        print()

    def get_word_prob(self, word1, word2):
        try:
            w1_w2 = 1e-8
            if word2 in self.dict[word1]["words"]:
                w1_w2 = self.dict[word1]["words"][word2]
            return w1_w2 * self.dict[word1]["freq"]
        except Exception:
            return self.default_frequency

    def get_probability(self, query):
        # there isn't words in dictionary
        if len(query) == 0:
            return 0
        if len(query) == 1 and not query[0] in self.dict:
            return 0

        # word chain
        # P(query) = P(w_1,...,w_n) = P(w_1|w_2) * P(w_2|w_3) * ... * P(w_n)
        prob = 1
        for i in range(len(query) - 1):
            word1 = query[i]
            word2 = query[i + 1]
            prob *= self.get_word_prob(word1, word2)

        if query[-1] in self.dict:
            prob *= self.dict[query[-1]]["freq"]

        return prob * len(query)

    def get_word_probability(self, word):
        if word in self.dict:
            return self.dict[word]["freq"]
        else:
            return 0.
