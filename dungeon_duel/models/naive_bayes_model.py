from sklearn.naive_bayes import GaussianNB
import numpy as np

class NaiveBayesPlayerPredictor:
    def __init__(self):
        self.model = GaussianNB()
        self.trained = False

    def fit(self, X, y):
        self.model.fit(X, y)
        self.trained = True

    def predict(self, X):
        if not self.trained:
            return None
        return self.model.predict(X)
