import pandas as pd
import matplotlib.pyplot as plt

def plot_monthly_sales(df_sales: pd.DataFrame, output_path: str):
    df = df_sales.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    grouped = df.groupby("month").agg(
        total_revenue=("revenue", "sum"),
        transactions=("transaction_id", "nunique")
    )
    grouped["avg_order_value"] = grouped["total_revenue"] / grouped["transactions"]

    plt.figure()
    grouped["total_revenue"].plot()
    plt.title("Total Revenue per Month")
    plt.xlabel("Month")
    plt.ylabel("Revenue")
    plt.tight_layout()
    plt.savefig(output_path.replace(".pdf", "_revenue.png"))
    plt.close()

    # Аналогично можно сохранить другие графики
    return grouped
