import itertools


class GrammarGenerator:

    def __init__(self, em, lm):
        self.em = em
        self.lm = lm

    def generate_correction(self, words):

        decart_of_correction = []

        for i in range(len(words)):
            word = words[i]
            decart_of_correction.append([])

            if word in self.lm.dict:
                decart_of_correction[i].append(word)
                continue

            word_correction = self.em.get_correction(word, max_lev=1)

            for w, lev in word_correction:
                decart_of_correction[-1].append(w)

            if word in self.lm.dict or len(decart_of_correction[i]) == 0:
                decart_of_correction[i].append(word)

        correction = itertools.product(*decart_of_correction)

        return correction

    def fix(self, query, word_idx):
        correction_words = self.em.get_correction(query[word_idx])
        if len(correction_words) == 0:
            return query
