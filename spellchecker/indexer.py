from bor import BorTree
from language_model import LanguageModel
from utils import save_obj
from error_model import ErrorModel
import sys

if __name__ == "__main__":
    sys.setrecursionlimit(50000)
    query_file = "queries_all.txt"

    print('language model is training')
    lm = LanguageModel(query_file)
    save_obj(lm, "LanguageModel")

    trie = BorTree(lm.dict.keys())

    print('\nerror model is training')
    em = ErrorModel(trie, query_file)
    save_obj(em, "ErrorModel")
