import itertools


keyboard = {
        'й': 'q', 'ц': 'w', 'у': 'e', 'к': 'r', 'е': 't', 'н': 'y', 'г': 'u',
        'ш': 'i', 'щ': 'o', 'з': 'p', 'х': '[', 'ъ': ']', 'ф': 'a', 'ы': 's',
        'в': 'd', 'а': 'f', 'п': 'g', 'р': 'h', 'о': 'j', 'л': 'k', 'д': 'l',
        'ж': ';', 'э': "'", 'я': 'z', 'ч': 'x', 'с': 'c', 'м': 'v', 'и': 'b',
        'т': 'n', 'ь': 'm', 'б': ',', 'ю': '.', 'q': 'й', 'w': 'ц', 'e': 'у',
        'r': 'к', 't': 'е', 'y': 'н', 'u': 'г', 'i': 'ш', 'o': 'щ', 'p': 'з',
        '[': 'х', ']': 'ъ', 'a': 'ф', 's': 'ы', 'd': 'в', 'f': 'а', 'g': 'п',
        'h': 'р', 'j': 'о', 'k': 'л', 'l': 'д', ';': 'ж', "'": 'э', 'z': 'я',
        'x': 'ч', 'c': 'с', 'v': 'м', 'b': 'и', 'n': 'т', 'm': 'ь', ',': 'б', '.': 'ю',
    }


def gen_fix_grammar(lm, em, words):
    # [[corrections of word_1],...,[corrections of word_n]]
    corrections = []
    for word in words:
        # it's right word
        if word in lm.dict:
            corrections.append([word])
            continue
        corrections.append([])
        correction = em.get_correction(word, max_lev=1)
        for w, _ in correction:
            corrections[-1].append(w)
        # we can't fix this word
        if len(corrections[-1]) == 0:
            corrections[-1].append(word)
    # all combinations of all possible fixes
    return itertools.product(*corrections)


def gen_fix_layout(words):
    query = []
    for word in words:
        new_word = ""
        for char in word:
            try:
                new_word += keyboard[char]
            except Exception:
                new_word += char
        query.append(new_word)
    return query


def gen_fix_join(words):
    if len(words) < 2:
        return words
    joins = []
    for i in range(len(words) - 1):
        join = words[0:i]
        join.append(words[i] + words[i + 1])
        join.extend(words[i + 2:])
        joins.append(join)
    return joins


def gen_fix_split(lm, words):
    splits = []
    for i in range(len(words)):
        word = words[i]
        if word in lm.dict:
            continue
        for j in range(1, len(word)):
            split = words[0:i]
            split.append(word[0:j])
            split.append(word[j:])
            split.extend(words[i + 1:])
            splits.append(split)
    return splits
