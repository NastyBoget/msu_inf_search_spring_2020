from language_model import LanguageModel
from error_model import ErrorModel
from bor import BorTree

queries_filename = 'queries_all.txt'
language_model_unigrams_filename = 'models/language_model_unigrams.pkl'
language_model_bigrams_filename = 'models/language_model_bigrams.pkl'
error_model_unigrams_filename = 'models/error_model_unigrams.pkl'
error_model_bigrams_filename = 'models/error_model_bigrams.pkl'
tree_model_filename = 'models/tree_model.pkl'

model = LanguageModel()
model.fit(queries_filename)
model.save_model(language_model_unigrams_filename, language_model_bigrams_filename)
print('language model saved')

model = ErrorModel()
model.fit(queries_filename)
model.save_model(error_model_unigrams_filename, error_model_bigrams_filename)
print('error model saved')

model = BorTree()
model.fit(language_model_unigrams_filename)
model.save_model(tree_model_filename)
print('bor tree saved')
