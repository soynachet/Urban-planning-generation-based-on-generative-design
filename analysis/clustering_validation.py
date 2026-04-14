import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score

# cargar CSV
X = np.loadtxt("clustering_features_normalized.csv", delimiter=",")

results = []

for k in [4,5,6,7]:
    kmeans = KMeans(n_clusters=k, random_state=42)
    labels = kmeans.fit_predict(X)

    sil = silhouette_score(X, labels)
    dbi = davies_bouldin_score(X, labels)

    results.append((k, sil, dbi))

# imprimir tabla
for r in results:
    print(f"K={r[0]} | silhouette={r[1]:.3f} | DBI={r[2]:.3f}")
