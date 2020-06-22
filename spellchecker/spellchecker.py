from bor import BorTree
from error_model import ErrorModel
from language_model import LanguageModel
from indexer import language_model_unigrams_filename, language_model_bigrams_filename, \
    error_model_unigrams_filename, error_model_bigrams_filename, tree_model_filename

LOOP = 10
ALPHA = 0.5
REFLECT_POW = 1 / 5  # for small numbers
e_model = ErrorModel()
e_model.load_bigram(error_model_bigrams_filename)

l_model = LanguageModel()
l_model.load_unigram(language_model_unigrams_filename)
l_model.load_bigram(language_model_bigrams_filename)


def fix_score(_fix, distance, orig_popularity):
    probability = l_model.get_probability(' '.join(_fix), smooth=REFLECT_POW)

    print("{}: ---> P(orig|fix)={}, fix_pop={}, orig_pop={} |--> result={}".format(_fix,
                                                                                   ALPHA * distance,
                                                                                   probability,
                                                                                   orig_popularity,
                                                                                   ALPHA * distance *
                                                                                   probability))
    return ALPHA * distance * probability


def query_str_popularity(_str):
    probability = l_model.get_probability(_str, smooth=REFLECT_POW)
    return probability


def generate_fix_query(st_matrix):
    query_dict = {}
    min_key = 0

    def add_query(local_score, string):
        # находим цепочки с наибольшим score'ом
        nonlocal min_key
        if len(query_dict) <= QUERY_VARIANTS:
            query_dict[local_score] = string
            return
        if local_score < min_key:
            return
        min_key = min(query_dict)
        query_dict.pop(min_key)
        query_dict[local_score] = string

    def get_word_chain(string, local_score, index):
        if index + 1 >= len(st_matrix):
            add_query(local_score, string + [st_matrix[-1][0][0]])
            return
        for item in st_matrix[index]:
            get_word_chain(string + [item[0]],
                           local_score
                           + l_model.get_probability(str(st_matrix[index][0][0]) + ' '
                                                     + str(st_matrix[index + 1][0][0]), smooth=REFLECT_POW)
                           + item[1],
                           index + 1)

    get_word_chain([], 0, 0)
    return query_dict


bor = BorTree()
bor.load_model(tree_model_filename)
bor.init_models(language_model_unigrams_filename, error_model_unigrams_filename, error_model_bigrams_filename)
QUERY_VARIANTS = 5
WORD_VARIANTS = 5
while True:
    print("enter:")
    query = input()

    words_list = query.split(" ")
    variants = []
    for word in words_list:
        var_list = bor.find_best(word)[:WORD_VARIANTS]
        variants += [var_list]

    print(variants)
    best_query = ""
    max_score = 0
    a = generate_fix_query(variants)
    print("variant matrix: " + str(a))
    query_popularity = query_str_popularity(query)
    for key, one_variant in a.items():
        score = fix_score(_fix=one_variant, distance=key, orig_popularity=query_popularity)
        if score > max_score:
            max_score = score
            best_query = one_variant

    print(best_query)
    print(' '.join(best_query[:]))
