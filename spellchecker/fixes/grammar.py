import itertools


class GrammarGenerator:

    def __init__(self, em, lm):
        self.em = em
        self.lm = lm

    def generate_correction(self, words):
        # [[corrections of word_1],...,[corrections of word_n]]
        corrections = []

        for word in words:
            # it's right word
            if word in self.lm.dict:
                corrections.append([word])
                continue

            corrections.append([])
            correction = self.em.get_correction(word, max_lev=1)

            for w, _ in correction:
                corrections[-1].append(w)

            # we can't fix this word
            if len(corrections[-1]) == 0:
                corrections[-1].append(word)
        # all combinations of all possible fixes
        return itertools.product(*corrections)

    def fix(self, query, word_idx):
        correction = self.em.get_correction(query[word_idx])
        if len(correction) == 0:
            return query
