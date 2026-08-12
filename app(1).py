
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Customer Engagement & Retention Analytics", page_icon="🏦", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("data/European_Bank.csv")
    df["BalanceSalaryRatio"] = df["Balance"] / df["EstimatedSalary"].replace(0, np.nan)
    median_balance = df["Balance"].median()
    df["EngagementProfile"] = np.select(
        [
            (df["IsActiveMember"] == 1) & (df["NumOfProducts"] >= 2),
            (df["IsActiveMember"] == 1) & (df["NumOfProducts"] == 1),
            (df["IsActiveMember"] == 0) & (df["Balance"] >= median_balance),
            (df["IsActiveMember"] == 0) & (df["NumOfProducts"] >= 2),
        ],
        ["Active Engaged", "Active Low Product", "Inactive High Balance", "Inactive Multi-Product"],
        default="Other",
    )
    df["RelationshipStrengthScore"] = (
        df["IsActiveMember"] * 40
        + np.clip(df["NumOfProducts"], 0, 2) / 2 * 30
        + df["HasCrCard"] * 10
        + (df["Tenure"] >= 5).astype(int) * 10
        + (df["Balance"] > df["EstimatedSalary"]).astype(int) * 10
    ).round(0)
    return df

df = load_data()

st.title("🏦 Customer Engagement & Product Utilization Analytics")
st.caption("Retention strategy dashboard | Unified Mentor Internship | D. H. L. N. S. Sri Vaishnavi")

with st.sidebar:
    st.header("Customer Filters")
    engagement = st.multiselect(
        "Engagement profile",
        sorted(df["EngagementProfile"].unique()),
        default=sorted(df["EngagementProfile"].unique())
    )
    min_products, max_products = int(df.NumOfProducts.min()), int(df.NumOfProducts.max())
    products = st.slider("Number of products", min_products, max_products, (min_products, max_products))
    balance_threshold = st.number_input("Minimum balance", min_value=0.0, value=0.0, step=5000.0)
    salary_threshold = st.number_input("Minimum estimated salary", min_value=0.0, value=0.0, step=5000.0)

filtered = df[
    df["EngagementProfile"].isin(engagement)
    & df["NumOfProducts"].between(products[0], products[1])
    & (df["Balance"] >= balance_threshold)
    & (df["EstimatedSalary"] >= salary_threshold)
]

def pct(x):
    return f"{x*100:.1f}%"

overall_churn = filtered["Exited"].mean() if len(filtered) else 0
active_retention = 1 - filtered.loc[filtered.IsActiveMember == 1, "Exited"].mean() if (filtered.IsActiveMember == 1).any() else 0
high_bal = (filtered["Balance"] >= df["Balance"].quantile(.75)) & (filtered["IsActiveMember"] == 0)
high_bal_rate = high_bal.mean() if len(filtered) else 0
card_stickiness = 1 - filtered.loc[filtered.HasCrCard == 1, "Exited"].mean() if (filtered.HasCrCard == 1).any() else 0
strength = filtered["RelationshipStrengthScore"].mean() if len(filtered) else 0

c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Customers", f"{len(filtered):,}")
c2.metric("Churn Rate", pct(overall_churn))
c3.metric("Engagement Retention", pct(active_retention))
c4.metric("High-Balance Disengagement", pct(high_bal_rate))
c5.metric("Relationship Strength", f"{strength:.1f}/100")

tab1, tab2, tab3, tab4 = st.tabs([
    "Engagement vs Churn", "Product Utilization", "High-Value Disengaged", "Retention Strength"
])

with tab1:
    st.subheader("Engagement vs Churn Overview")
    activity = filtered.groupby("IsActiveMember").agg(Customers=("CustomerId","count"), Churn_Rate=("Exited","mean")).reset_index()
    activity["Status"] = activity["IsActiveMember"].map({0:"Inactive",1:"Active"})
    st.bar_chart(activity.set_index("Status")["Churn_Rate"])
    st.dataframe(activity[["Status","Customers","Churn_Rate"]].style.format({"Churn_Rate":"{:.1%}"}), use_container_width=True)
    st.info("Use this view to identify whether inactivity is associated with higher churn in the selected customer population.")

with tab2:
    st.subheader("Product Utilization Impact Analysis")
    prod = filtered.groupby("NumOfProducts").agg(Customers=("CustomerId","count"), Churn_Rate=("Exited","mean")).reset_index()
    st.line_chart(prod.set_index("NumOfProducts")["Churn_Rate"])
    st.dataframe(prod.style.format({"Churn_Rate":"{:.1%}"}), use_container_width=True)
    st.info("Product depth should be interpreted with context: very high product counts may represent unusual or potentially problematic cases, so they should be investigated rather than assumed to be automatically loyal.")

with tab3:
    st.subheader("High-Value Disengaged Customer Detector")
    q75 = df["Balance"].quantile(.75)
    hv = filtered[(filtered["Balance"] >= q75) & (filtered["IsActiveMember"] == 0)].copy()
    st.write(f"High-value threshold used: balance at or above the dataset 75th percentile ({q75:,.2f}).")
    st.metric("High-value disengaged customers", f"{len(hv):,}")
    if len(hv):
        hv["Priority"] = np.select(
            [hv["Exited"].eq(1), hv["RelationshipStrengthScore"].lt(50)],
            ["Churned", "At Risk"],
            default="Monitor"
        )
        cols = ["CustomerId","Geography","Age","Balance","EstimatedSalary","NumOfProducts","HasCrCard","IsActiveMember","Exited","RelationshipStrengthScore","Priority"]
        st.dataframe(hv[cols].sort_values(["Priority","Balance"], ascending=[True,False]), use_container_width=True)
    else:
        st.success("No customers meet the current high-value disengagement criteria.")

with tab4:
    st.subheader("Retention Strength Scoring")
    st.write("The score is a transparent business-rule index for prioritization, not a machine-learning probability.")
    score_bins = pd.cut(filtered["RelationshipStrengthScore"], bins=[-1,39,59,79,100], labels=["Low","Moderate","Strong","Very Strong"])
    score_summary = filtered.assign(StrengthTier=score_bins).groupby("StrengthTier", observed=False).agg(
        Customers=("CustomerId","count"), Churn_Rate=("Exited","mean")
    ).reset_index()
    st.bar_chart(score_summary.set_index("StrengthTier")["Churn_Rate"])
    st.dataframe(score_summary.style.format({"Churn_Rate":"{:.1%}"}), use_container_width=True)

st.divider()
st.caption("Project developed for academic/internship demonstration. Dataset is used for analytics and does not represent live banking customers.")
