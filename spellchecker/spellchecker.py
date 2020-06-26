from classifier.classifier import QueryClassifier
from fixes.grammar import GrammarGenerator
from fixes.join import JoinGenerator
from fixes.layout import LayoutGenerator
from fixes.split import SplitGenerator
from utils import TextFormatter, load_obj


def fix_layout(layout, words, correction, probs):
    changed_words = layout.generate_correction(words)
    all_generation.append(changed_words)
    formatted_query = textFormatter.format_text(changed_words)
    if qc.is_correct(formatted_query, changed_words):
        correction.append(formatted_query)
        probs.append(lm.get_probability(changed_words))


def fix_grammar(grammar, words, correction, probs):
    grammas = grammar.generate_correction(words)
    for gramma in grammas:
        all_generation.append(gramma)
        formatted_query = textFormatter.format_text(gramma)
        if qc.is_correct(formatted_query, gramma):
            correction.append(formatted_query)
            probs.append(lm.get_probability(gramma))


def fix_join(join, words, correction, probs):
    joins = join.generate_joins(words)
    all_generation.extend(joins)
    for join in joins:
        changed_query = " ".join(join)
        if qc.is_correct(changed_query, join):
            correction.append(changed_query)
            probs.append(lm.get_probability(join))


def fix_split(split, words, correction, probs):
    splits = split.generate_splits(words)
    all_generation.extend(splits)
    for split in splits:
        changed_query = " ".join(split)
        if qc.is_correct(changed_query, split):
            correction.append(changed_query)
            probs.append(lm.get_probability(split))


def correct(layout, grammar, join, split, words, correction, probs):
    fix_layout(layout, words, correction, probs)
    fix_grammar(grammar, words, correction, probs)
    fix_join(join, words, correction, probs)
    fix_split(split, words, correction, probs)


if __name__ == "__main__":

    MAX_ITER = 2

    lm = load_obj("LanguageModel")
    em = load_obj("ErrorModel")
    qc = QueryClassifier(load_obj("Classifier"), lm)

    layoutGenerator = LayoutGenerator()
    splitGenerator = SplitGenerator(lm)
    joinGenerator = JoinGenerator()
    grammarGenerator = GrammarGenerator(em, lm)

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

                correct(layoutGenerator, grammarGenerator, joinGenerator, splitGenerator,
                        words, correction, probabilities)

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
