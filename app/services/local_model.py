import math
import pickle
import random


def _mean(col):
    return sum(col) / len(col) if col else 0.0


def _std(col, mu):
    var = sum((x - mu) ** 2 for x in col) / max(len(col), 1)
    return math.sqrt(var) or 1.0


class LogRegModel:
    def __init__(self):
        self.means = []
        self.stds = []
        self.coef_ = []
        self.intercept_ = 0.0
        self.classes_ = [0, 1]

    def _scale_row(self, row):
        return [(x - m) / s for x, m, s in zip(row, self.means, self.stds)]

    def fit(self, X, y, steps=400, lr=0.15):
        n = len(X)
        d = len(X[0])
        cols = list(zip(*X))
        self.means = [_mean(list(c)) for c in cols]
        self.stds = [_std(list(c), m) for c, m in zip(cols, self.means)]
        xs = [self._scale_row(r) for r in X]
        pos = max(sum(y), 1)
        neg = max(n - sum(y), 1)
        w = [0.0] * d
        b = 0.0
        for _ in range(steps):
            gw = [0.0] * d
            gb = 0.0
            for row, yi in zip(xs, y):
                z = b + sum(wi * xi for wi, xi in zip(w, row))
                p = 1 / (1 + math.exp(-max(min(z, 20), -20)))
                wt = n / (2 * pos) if yi == 1 else n / (2 * neg)
                err = (p - yi) * wt
                gb += err
                for j in range(d):
                    gw[j] += err * row[j]
            b -= lr * gb / n
            w = [wj - lr * g / n for wj, g in zip(w, gw)]
        self.coef_ = w
        self.intercept_ = b
        return self

    def predict_proba_one(self, row):
        xs = self._scale_row(row)
        z = self.intercept_ + sum(wi * xi for wi, xi in zip(self.coef_, xs))
        p = 1 / (1 + math.exp(-max(min(z, 20), -20)))
        return p

    def predict_one(self, row):
        return int(self.predict_proba_one(row) >= 0.5)


def stratified_split(X, y, test_size=0.25, seed=42):
    rng = random.Random(seed)
    by = {0: [], 1: []}
    for i, yi in enumerate(y):
        by[int(yi)].append(i)
    train_i, test_i = [], []
    for cls, idxs in by.items():
        rng.shuffle(idxs)
        n_test = max(1, int(len(idxs) * test_size)) if idxs else 0
        test_i.extend(idxs[:n_test])
        train_i.extend(idxs[n_test:])
    if not train_i:
        train_i, test_i = test_i[:1], test_i[1:]
    return [X[i] for i in train_i], [X[i] for i in test_i], [y[i] for i in train_i], [y[i] for i in test_i]


def metrics_from(y_true, y_pred, y_prob):
    tp = sum(1 for a, b in zip(y_true, y_pred) if a == 1 and b == 1)
    tn = sum(1 for a, b in zip(y_true, y_pred) if a == 0 and b == 0)
    fp = sum(1 for a, b in zip(y_true, y_pred) if a == 0 and b == 1)
    fn = sum(1 for a, b in zip(y_true, y_pred) if a == 1 and b == 0)
    acc = (tp + tn) / max(len(y_true), 1)
    prec = tp / max(tp + fp, 1)
    rec = tp / max(tp + fn, 1)
    f1 = 2 * prec * rec / max(prec + rec, 1e-9)
    auc = None
    if len(set(y_true)) == 2:
        pairs = sorted(zip(y_prob, y_true), reverse=True)
        pos = sum(y_true)
        neg = len(y_true) - pos
        tps = fps = 0
        prev = None
        points = [(0.0, 0.0)]
        for p, yi in pairs:
            if prev is not None and p != prev:
                points.append((fps / neg, tps / pos))
            if yi == 1:
                tps += 1
            else:
                fps += 1
            prev = p
        points.append((1.0, 1.0))
        auc = 0.0
        for i in range(1, len(points)):
            x0, y0 = points[i - 1]
            x1, y1 = points[i]
            auc += (x1 - x0) * (y0 + y1) / 2
    return {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "roc_auc": auc,
        "confusion_matrix": [[tn, fp], [fn, tp]],
    }


def dump_model(path, payload):
    with open(path, "wb") as f:
        pickle.dump(payload, f)


def load_model(path):
    with open(path, "rb") as f:
        return pickle.load(f)
