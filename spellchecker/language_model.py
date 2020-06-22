import re


class LanguageModel:

    def __init__(self, filename):
        self.dict = {}
        self.__count_of_word = 0.
        self._regex = re.compile(r"\w+")
        self.__fit(filename)
        self.__normalize()

    def __fit(self, filename):
        with open(filename) as f:
            content = f.readlines()
        num_line = 0
        for line in content:
            num_line += 1
            print(f"\r{num_line} lines are processed...", end='', flush=True)
            line = line.lower()
            line = line[:-1]
            index = line.find('\t')
            if index > 0:
                line = line[index+1:]

            words = re.findall(r"(?u)\w+", line)
            for i in range(len(words)):
                word = words[i]
                if word in self.dict:
                    self.dict[word]["freq"] += 1.
                else:
                    self.dict[word] = {"freq": 1.,
                                       "words": {}}
                self.__count_of_word += 1

                if i != len(words) - 1:
                    if words[i + 1] in self.dict[word]["words"]:
                        self.dict[word]["words"][words[i + 1]] += 1.
                    else:
                        self.dict[word]["words"][words[i + 1]] = 1.
        print()

    def __normalize(self):
        for key, value in self.dict.items():
            value["freq"] /= self.__count_of_word
            count_of_uses = sum(value["words"].values())
            for word, freq in value["words"].items():
                value["words"][word] /= count_of_uses

    def __get_word_prob(self, w1, w2):
        try:
            w2_prob = 1e-8
            if w2 in self.dict[w1]["words"]:
                w2_prob = self.dict[w1]["words"][w2]
            return self.dict[w1]["freq"] * w2_prob
        except Exception:
            return 1e-28

    def get_prob(self, query):
        if len(query) == 0:
            return 0.
        if len(query) == 1 and not query[-1] in self.dict:
            return 0.

        prob = 1.
        for i in range(len(query) - 1):
            w1 = query[i]
            w2 = query[i + 1]
            prob *= self.__get_word_prob(w1, w2)

        if query[-1] in self.dict:
            prob *= self.dict[query[-1]]["freq"]

        return prob*len(query)

    def get_word_prob(self, word):
        if word in self.dict:
            return self.dict[word]["freq"]
        else:
            return 0.
