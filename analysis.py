
import pandas as pd
import numpy as np

def load_and_validate(path="data/European_Bank.csv"):
    df = pd.read_csv(path)
    required = [
        "CustomerId","Surname","CreditScore","Geography","Gender","Age",
        "Tenure","Balance","NumOfProducts","HasCrCard",
        "IsActiveMember","EstimatedSalary","Exited"
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    for col in ["HasCrCard", "IsActiveMember", "Exited"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    df["BalanceSalaryRatio"] = df["Balance"] / df["EstimatedSalary"].replace(0, np.nan)
    return df

def add_segments(df):
    df = df.copy()
    median_balance = df["Balance"].median()
    df["EngagementProfile"] = np.select(
        [
            (df["IsActiveMember"] == 1) & (df["NumOfProducts"] >= 2),
            (df["IsActiveMember"] == 1) & (df["NumOfProducts"] == 1),
            (df["IsActiveMember"] == 0) & (df["Balance"] >= median_balance),
            (df["IsActiveMember"] == 0) & (df["NumOfProducts"] >= 2),
        ],
        [
            "Active Engaged",
            "Active Low Product",
            "Inactive High Balance",
            "Inactive Multi-Product",
        ],
        default="Other",
    )
    # Transparent business-rule score for dashboard prioritization.
    df["RelationshipStrengthScore"] = (
        df["IsActiveMember"] * 40
        + np.clip(df["NumOfProducts"], 0, 2) / 2 * 30
        + df["HasCrCard"] * 10
        + (df["Tenure"] >= 5).astype(int) * 10
        + (df["Balance"] > df["EstimatedSalary"]).astype(int) * 10
    ).round(0)
    return df

def kpis(df):
    q75 = df["Balance"].quantile(.75)
    high_value_disengaged = (df["Balance"] >= q75) & (df["IsActiveMember"] == 0)
    return {
        "engagement_retention_ratio": 1 - df.loc[df.IsActiveMember == 1, "Exited"].mean(),
        "product_depth_index": df["NumOfProducts"].mean() / 2,
        "high_balance_disengagement_rate": high_value_disengaged.mean(),
        "credit_card_stickiness": 1 - df.loc[df.HasCrCard == 1, "Exited"].mean(),
        "relationship_strength_index": df["RelationshipStrengthScore"].mean(),
    }

if __name__ == "__main__":
    df = add_segments(load_and_validate())
    print(df.describe(include="all"))
    print("\nChurn by activity:\n", df.groupby("IsActiveMember")["Exited"].mean())
    print("\nChurn by product count:\n", df.groupby("NumOfProducts")["Exited"].mean())
    print("\nChurn by engagement profile:\n", df.groupby("EngagementProfile")["Exited"].mean().sort_values(ascending=False))
    print("\nKPIs:\n", kpis(df))
