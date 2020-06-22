from classifier.features import FeatureGenerator


class QueryClassifier:

    def __init__(self, clf, lm):
        self.clf = clf
        self.fg = FeatureGenerator(lm)

    def is_correct(self, query, words):
        x = [self.fg.generate_features(query, words)]
        return self.clf.predict(x)[0]
