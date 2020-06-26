from classifier import QueryClassifier
from utils import TextFormatter, load_obj
from fixes import gen_fix_grammar, gen_fix_layout, gen_fix_join, gen_fix_split


def correct(lm, em, qc, words, all_generation, correction, probs):
    # layout fixing
    changed_words = gen_fix_layout(words)
    all_generation.append(changed_words)
    formatted_query = textFormatter.format_text(changed_words)
    if qc.is_correct(formatted_query, changed_words):
        correction.append(formatted_query)
        probs.append(lm.get_probability(changed_words))

    # grammar fixing
    grammas = gen_fix_grammar(lm, em, words)
    for gramma in grammas:
        all_generation.append(gramma)
        formatted_query = textFormatter.format_text(gramma)
        if qc.is_correct(formatted_query, gramma):
            correction.append(formatted_query)
            probs.append(lm.get_probability(gramma))

    # join fixing
    joins = gen_fix_join(words)
    all_generation.extend(joins)
    for join in joins:
        changed_query = " ".join(join)
        if qc.is_correct(changed_query, join):
            correction.append(changed_query)
            probs.append(lm.get_probability(join))

    # split fixing
    splits = gen_fix_split(lm, words)
    all_generation.extend(splits)
    for split in splits:
        changed_query = " ".join(split)
        if qc.is_correct(changed_query, split):
            correction.append(changed_query)
            probs.append(lm.get_probability(split))


if __name__ == "__main__":

    MAX_ITER = 2

    lm = load_obj("LanguageModel")
    em = load_obj("ErrorModel")
    qc = QueryClassifier(load_obj("Classifier"), lm)

    while True:
        s = input()
        textFormatter = TextFormatter(s)
        words = textFormatter.get_query_list()
        query = textFormatter.text
        if qc.is_correct(query, words):
            print(query)
        else:
            iteration = MAX_ITER
            found = False
            while iteration > 0 and not found:
                iteration -= 1

                correction = []
                all_generation = []
                probabilities = []

                correct(lm, em, qc, words, all_generation, correction, probabilities)

                if len(correction) != 0:
                    print(correction[probabilities.index(max(probabilities))])
                    found = True
                else:
                    gen_prob = []
                    for g in all_generation:
                        gen_prob.append(lm.get_probability(g))
                    words = all_generation[gen_prob.index(max(gen_prob))]
                    words = list(words)

            if not found:
                print(textFormatter.format_text(words))
