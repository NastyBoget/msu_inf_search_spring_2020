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

    tree = BorTree(lm.dict.keys())

    print('error model is training')
    em = ErrorModel(tree, query_file)
    save_obj(em, "ErrorModel")
