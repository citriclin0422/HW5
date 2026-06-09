import warnings

import matplotlib
import numpy as np
import streamlit as st
from matplotlib.colors import ListedColormap
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs, make_circles, make_classification, make_moons
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, mean_squared_error, silhouette_score
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier, plot_tree

matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLUE = "#2448f5"
RED = "#ff4b4b"
PALETTE = ["#2448f5", "#ff4b4b", "#16a085", "#f39c12", "#8e44ad", "#00a8cc"]


def _slider(slug, name, label, minimum, maximum, value, step=None, help_text=None):
    kwargs = {"key": f"{slug}_{name}", "help": help_text}
    if step is not None:
        kwargs["step"] = step
    return st.slider(label, minimum, maximum, value, **kwargs)


def _style_axis(ax, title, xlabel="Feature 1", ylabel="Feature 2"):
    ax.set_title(title, fontsize=11)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.16)


def _classification_data(kind, n_points, noise, separation=1.5):
    if kind == "linear":
        return make_classification(
            n_samples=n_points,
            n_features=2,
            n_redundant=0,
            n_informative=2,
            n_clusters_per_class=1,
            class_sep=separation,
            flip_y=noise,
            random_state=42,
        )
    if kind == "circles":
        return make_circles(n_samples=n_points, noise=noise, factor=0.45, random_state=42)
    return make_moons(n_samples=n_points, noise=noise, random_state=42)


def _draw_surface(ax, model, x, y, title, support_vectors=None):
    padding = 0.65
    x_min, x_max = x[:, 0].min() - padding, x[:, 0].max() + padding
    y_min, y_max = x[:, 1].min() - padding, x[:, 1].max() + padding
    xx, yy = np.meshgrid(
        np.linspace(x_min, x_max, 220),
        np.linspace(y_min, y_max, 220),
    )
    grid = np.c_[xx.ravel(), yy.ravel()]
    if hasattr(model, "predict_proba"):
        z = model.predict_proba(grid)[:, 1]
    else:
        decision = model.decision_function(grid)
        z = 1 / (1 + np.exp(-np.clip(decision, -20, 20)))
    z = z.reshape(xx.shape)

    ax.contourf(xx, yy, z, levels=np.linspace(0, 1, 12), cmap="RdBu_r", alpha=0.28)
    ax.contour(xx, yy, z, levels=[0.5], colors=[RED], linewidths=2)
    ax.scatter(
        x[:, 0],
        x[:, 1],
        c=y,
        cmap=ListedColormap([BLUE, RED]),
        edgecolors="white",
        linewidths=0.45,
        s=25,
        alpha=0.9,
    )
    if support_vectors is not None:
        ax.scatter(
            support_vectors[:, 0],
            support_vectors[:, 1],
            s=85,
            facecolors="none",
            edgecolors="#111827",
            linewidths=1.2,
            label="Support vectors",
        )
        ax.legend(loc="best", fontsize=8)
    _style_axis(ax, title)


def _decision_surface(model, x, y, title, support_vectors=None):
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    _draw_surface(ax, model, x, y, title, support_vectors)
    fig.tight_layout()
    return fig


def _show_result(metric_label, metric_value, fig, details, caption):
    st.metric(metric_label, metric_value)
    st.pyplot(fig, width="stretch")
    plt.close(fig)
    for label, value in details:
        st.write(f"**{label}:** {value}")
    st.caption(caption)


def _linear_regression(slug):
    with st.container():
        controls, chart = st.columns([0.46, 0.54], gap="large")
        with controls:
            n_points = _slider(slug, "n", "Select the number of data points (n):", 100, 1000, 882)
            variance = _slider(
                slug, "variance", "Select the variance (from 0 to 200):", 0.0, 200.0, 100.0, 1.0
            )
            a = _slider(slug, "a", "Select value for a", -10, 10, -7)
            b = _slider(slug, "b", "Select value for b", -100, 100, 52)

        rng = np.random.default_rng(42)
        x = rng.uniform(-2, 2, n_points)
        y = a * x + b + rng.normal(0, np.sqrt(variance), n_points)
        model = LinearRegression().fit(x.reshape(-1, 1), y)
        prediction = model.predict(x.reshape(-1, 1))
        mse = mean_squared_error(y, prediction)
        order = np.argsort(x)

        fig, ax = plt.subplots(figsize=(7.2, 4.8))
        ax.scatter(x, y, color=BLUE, s=13, alpha=0.78, label="True Data points")
        ax.plot(x[order], prediction[order], color=RED, linewidth=2.2, label="Regression line")
        ax.legend(loc="best", fontsize=8)
        _style_axis(ax, "Linear Regression Fit", "x", "y")
        fig.tight_layout()
        with chart:
            _show_result(
                "Mean Squared Error",
                f"{mse:.2f}",
                fig,
                [
                    ("Coefficient (slope)", f"{model.coef_[0]:.10f}"),
                    ("Intercept", f"{model.intercept_:.10f}"),
                ],
                "調整資料量、變異數與真實直線參數，觀察估計係數如何接近設定值。",
            )


def _classification_demo(slug, config):
    controls, chart = st.columns([0.46, 0.54], gap="large")
    with controls:
        n_points = _slider(slug, "n", "資料點數 (n)", 100, 800, 300, 10)
        noise = _slider(slug, "noise", "資料雜訊", 0.0, config["noise_max"], config["noise"], 0.01)
        values = {}
        for parameter in config["parameters"]:
            values[parameter["name"]] = _slider(
                slug,
                parameter["name"],
                parameter["label"],
                parameter["min"],
                parameter["max"],
                parameter["value"],
                parameter.get("step"),
                parameter.get("help"),
            )

    x, y = _classification_data(config["data"], n_points, noise, config.get("separation", 1.5))
    x = StandardScaler().fit_transform(x)
    model = config["factory"](values)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        model.fit(x, y)
    accuracy = accuracy_score(y, model.predict(x))
    support_vectors = getattr(model, "support_vectors_", None)
    fig = _decision_surface(model, x, y, f"{config['title']} Decision Boundary", support_vectors)
    details = config["details"](model, values)
    with chart:
        _show_result(
            "Training Accuracy",
            f"{accuracy:.2%}",
            fig,
            details,
            "背景顏色代表模型預測機率，紅線代表分類決策邊界。",
        )


def _decision_tree(slug):
    controls, chart = st.columns([0.46, 0.54], gap="large")
    with controls:
        n_points = _slider(slug, "n", "資料點數 (n)", 100, 800, 300, 10)
        noise = _slider(slug, "noise", "資料雜訊", 0.0, 0.40, 0.18, 0.01)
        depth = _slider(slug, "depth", "樹的最大深度", 1, 10, 4)
        leaf = _slider(slug, "leaf", "葉節點最少樣本數", 1, 30, 5)

    x, y = _classification_data("moons", n_points, noise)
    model = DecisionTreeClassifier(max_depth=depth, min_samples_leaf=leaf, random_state=42).fit(x, y)
    accuracy = accuracy_score(y, model.predict(x))
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.5))
    _draw_surface(axes[0], model, x, y, "Decision Boundary")
    plot_tree(model, ax=axes[1], max_depth=2, filled=True, fontsize=6, feature_names=["x1", "x2"])
    axes[1].set_title("Tree Structure (first 3 levels)", fontsize=11)
    fig.tight_layout()
    with chart:
        _show_result(
            "Training Accuracy",
            f"{accuracy:.2%}",
            fig,
            [("實際樹深", model.get_depth()), ("葉節點數", model.get_n_leaves())],
            "左圖顯示切分邊界，右圖顯示前幾層決策規則。",
        )


def _kmeans(slug):
    controls, chart = st.columns([0.46, 0.54], gap="large")
    with controls:
        n_points = _slider(slug, "n", "資料點數 (n)", 100, 1000, 400, 10)
        spread = _slider(slug, "spread", "群集分散程度", 0.30, 2.50, 0.85, 0.05)
        clusters = _slider(slug, "clusters", "群集數量 (K)", 2, 6, 3)
        iterations = _slider(slug, "iterations", "最大迭代次數", 10, 300, 100, 10)

    x, _ = make_blobs(n_samples=n_points, centers=clusters, cluster_std=spread, random_state=42)
    model = KMeans(n_clusters=clusters, max_iter=iterations, n_init=10, random_state=42).fit(x)
    score = silhouette_score(x, model.labels_)
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.scatter(x[:, 0], x[:, 1], c=model.labels_, cmap="tab10", s=22, alpha=0.78)
    ax.scatter(
        model.cluster_centers_[:, 0],
        model.cluster_centers_[:, 1],
        marker="X",
        s=190,
        c="#111827",
        edgecolors="white",
        linewidths=1.2,
        label="Centroids",
    )
    ax.legend(loc="best", fontsize=8)
    _style_axis(ax, "K-Means Clustering Result")
    fig.tight_layout()
    with chart:
        _show_result(
            "Silhouette Score",
            f"{score:.3f}",
            fig,
            [("Inertia", f"{model.inertia_:.2f}"), ("實際迭代次數", model.n_iter_)],
            "不同顏色代表模型找到的群集，X 標記為群中心。",
        )


def _pca(slug):
    controls, chart = st.columns([0.46, 0.54], gap="large")
    with controls:
        n_points = _slider(slug, "n", "資料點數 (n)", 100, 1000, 400, 10)
        dimensions = _slider(slug, "dimensions", "原始特徵維度", 3, 12, 6)
        components = _slider(slug, "components", "保留主成分數", 1, 3, 2)
        noise = _slider(slug, "noise", "資料雜訊", 0.0, 1.0, 0.25, 0.01)

    rng = np.random.default_rng(42)
    latent = rng.normal(size=(n_points, 2))
    weights = rng.normal(size=(2, dimensions))
    x = latent @ weights + rng.normal(scale=noise, size=(n_points, dimensions))
    scaled = StandardScaler().fit_transform(x)
    model = PCA(n_components=min(components, dimensions)).fit(scaled)
    projected = model.transform(scaled)
    display_y = projected[:, 1] if projected.shape[1] > 1 else np.zeros(n_points)
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.scatter(projected[:, 0], display_y, c=latent[:, 0], cmap="viridis", s=22, alpha=0.78)
    _style_axis(ax, "PCA Projection", "Principal Component 1", "Principal Component 2")
    fig.tight_layout()
    explained = model.explained_variance_ratio_.sum()
    ratios = ", ".join(f"PC{i + 1}: {ratio:.1%}" for i, ratio in enumerate(model.explained_variance_ratio_))
    with chart:
        _show_result(
            "Explained Variance",
            f"{explained:.2%}",
            fig,
            [("各主成分解釋率", ratios), ("輸出維度", projected.shape[1])],
            "投影後仍保留越高的解釋變異，代表降維損失越少。",
        )


CLASSIFIERS = {
    "logistic-regression": {
        "title": "Logistic Regression",
        "data": "linear",
        "noise": 0.06,
        "noise_max": 0.35,
        "parameters": [
            {"name": "c", "label": "正則化參數 C", "min": 0.1, "max": 10.0, "value": 1.0, "step": 0.1},
            {"name": "threshold", "label": "分類門檻", "min": 0.1, "max": 0.9, "value": 0.5, "step": 0.01},
        ],
        "factory": lambda p: ThresholdLogisticRegression(c=p["c"], threshold=p["threshold"]),
        "details": lambda model, _: [
            ("係數", np.array2string(model.coef_[0], precision=3)),
            ("截距", f"{model.intercept_[0]:.3f}"),
        ],
    },
    "random-forest": {
        "title": "Random Forest",
        "data": "moons",
        "noise": 0.20,
        "noise_max": 0.45,
        "parameters": [
            {"name": "trees", "label": "決策樹數量", "min": 10, "max": 200, "value": 80, "step": 10},
            {"name": "depth", "label": "每棵樹最大深度", "min": 1, "max": 12, "value": 5},
        ],
        "factory": lambda p: RandomForestClassifier(
            n_estimators=p["trees"], max_depth=p["depth"], random_state=42, n_jobs=-1
        ),
        "details": lambda model, _: [
            ("實際樹數", len(model.estimators_)),
            ("特徵重要性", np.array2string(model.feature_importances_, precision=3)),
        ],
    },
    "svm": {
        "title": "Support Vector Machine",
        "data": "circles",
        "noise": 0.10,
        "noise_max": 0.30,
        "parameters": [
            {"name": "c", "label": "懲罰參數 C", "min": 0.1, "max": 10.0, "value": 2.0, "step": 0.1},
            {"name": "gamma", "label": "RBF Gamma", "min": 0.1, "max": 5.0, "value": 1.0, "step": 0.1},
        ],
        "factory": lambda p: SVC(C=p["c"], gamma=p["gamma"], random_state=42),
        "details": lambda model, _: [("支持向量數", len(model.support_vectors_)), ("Kernel", "RBF")],
    },
    "knn": {
        "title": "K-Nearest Neighbors",
        "data": "moons",
        "noise": 0.20,
        "noise_max": 0.45,
        "parameters": [
            {"name": "neighbors", "label": "鄰居數量 (K)", "min": 1, "max": 30, "value": 7},
            {"name": "power", "label": "Minkowski 距離次方", "min": 1, "max": 3, "value": 2},
        ],
        "factory": lambda p: KNeighborsClassifier(n_neighbors=p["neighbors"], p=p["power"], weights="distance"),
        "details": lambda _, p: [("鄰居數", p["neighbors"]), ("距離", f"Minkowski p={p['power']}")],
    },
    "naive-bayes": {
        "title": "Gaussian Naive Bayes",
        "data": "linear",
        "noise": 0.08,
        "noise_max": 0.35,
        "separation": 1.25,
        "parameters": [
            {"name": "smooth", "label": "變異數平滑 (×10⁻⁹)", "min": 1, "max": 100, "value": 1},
        ],
        "factory": lambda p: GaussianNB(var_smoothing=p["smooth"] * 1e-9),
        "details": lambda model, _: [
            ("類別先驗機率", np.array2string(model.class_prior_, precision=3)),
            ("模型假設", "給定類別後，各特徵條件獨立"),
        ],
    },
    "neural-networks": {
        "title": "Neural Network",
        "data": "moons",
        "noise": 0.20,
        "noise_max": 0.45,
        "parameters": [
            {"name": "neurons", "label": "隱藏層神經元數", "min": 2, "max": 40, "value": 12, "step": 2},
            {"name": "epochs", "label": "最大訓練回合", "min": 50, "max": 500, "value": 250, "step": 50},
        ],
        "factory": lambda p: MLPClassifier(
            hidden_layer_sizes=(p["neurons"],),
            max_iter=p["epochs"],
            alpha=0.001,
            random_state=42,
        ),
        "details": lambda model, _: [("實際訓練回合", model.n_iter_), ("最終 Loss", f"{model.loss_:.4f}")],
    },
}


class ThresholdLogisticRegression(LogisticRegression):
    def __init__(self, c=1.0, threshold=0.5):
        super().__init__(C=c, random_state=42)
        self.c = c
        self.threshold = threshold

    def predict(self, x):
        return (self.predict_proba(x)[:, 1] >= self.threshold).astype(int)


def render_model_visualization(topic):
    slug = topic["slug"]
    st.markdown(f"## {topic['english']} with Streamlit")
    if slug == "linear-regression":
        _linear_regression(slug)
    elif slug == "decision-tree":
        _decision_tree(slug)
    elif slug == "k-means":
        _kmeans(slug)
    elif slug == "pca":
        _pca(slug)
    else:
        _classification_demo(slug, CLASSIFIERS[slug])
