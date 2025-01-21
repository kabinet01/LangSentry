import pickle

class BaselineManager:
    def __init__(self):
        self.baseline = None

    def load_baseline(self, path: str):
        with open(path, "rb") as f:
            self.baseline = pickle.load(f)

    def save_baseline(self, path: str):
        with open(path, "wb") as f:
            pickle.dump(self.baseline, f)

    def get_baseline(self):
        if not self.baseline:
            raise ValueError("Baseline not loaded!")
        return self.baseline
