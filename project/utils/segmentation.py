import pandas as pd
from sklearn.cluster import KMeans

def segment_customers(df: pd.DataFrame, n_clusters: int = 3) -> pd.DataFrame:
    """
    df должен содержать столбцы: customer_id, total_purchases, avg_purchase_value
    Возвращает df с добавленным столбцом cluster_label.
    """
    features = df[["total_purchases", "avg_purchase_value"]].fillna(0)
    model = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
    labels = model.fit_predict(features)
    df = df.copy()
    df["cluster_label"] = labels
    return df
