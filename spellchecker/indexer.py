from language_model import LanguageModel
from error_model import ErrorModel
from bor import BorTree

queries_filename = 'queries_all.txt'
language_model_unigrams_filename = 'models/language_model_unigrams.json'
language_model_bigrams_filename = 'models/language_model_bigrams.json'
error_model_unigrams_filename = 'models/error_model_unigrams.json'
error_model_bigrams_filename = 'models/error_model_bigrams.json'
tree_model_filename = 'models/tree_model.json'

model = LanguageModel()
model.fit(queries_filename)
model.to_json(language_model_unigrams_filename, language_model_bigrams_filename)

model = ErrorModel()
model.fit(queries_filename)
model.to_json(error_model_unigrams_filename, error_model_bigrams_filename)

model = BorTree()
model.fit(language_model_unigrams_filename, language_model_bigrams_filename)
model.to_json(tree_model_filename)
