# Customer Engagement and Product Utilization Analytics for Retention Strategy

**Student:** D. H. L. N. S. Sri Vaishnavi  
**Internship:** Unified Mentor  
**Project Type:** Customer analytics / retention strategy  
**Dataset:** European Bank customer dataset (10,000 records)

## Project objective
This project evaluates customer retention through engagement, product utilization and relationship strength. It focuses on whether activity and product depth provide stronger retention signals than financial strength alone.

## Main analyses
1. Engagement vs churn
2. Product count and churn
3. Financial commitment vs engagement
4. High-balance disengaged customer detection
5. Relationship strength scoring
6. Retention strategy recommendations

## Dashboard modules
- Engagement vs Churn Overview
- Product Utilization Impact Analysis
- High-Value Disengaged Customer Detector
- Retention Strength Scoring

## Dataset validation
The supplied CSV contains 10,000 customer records and 14 columns. Binary fields (`HasCrCard`, `IsActiveMember`, `Exited`) were checked for numeric 0/1 values.

## Key results from the supplied dataset
- Overall churn rate: **20.4%**
- Active-member churn rate: **14.3%**
- Inactive-member churn rate: **26.9%**
- Customers with 1 product churned at **27.7%**
- Customers with 2 products churned at **7.6%**
- High-balance disengaged customers: **12.5%** of the dataset
- Churn among high-balance disengaged customers: **30.5%**

## How to run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## GitHub structure
- `app.py` - Streamlit dashboard
- `analysis.py` - reusable analysis functions
- `requirements.txt` - Python dependencies
- `data/European_Bank.csv` - supplied dataset
- `assets/` - report/dashboard visuals
- `research_paper.pdf` - research paper
- `executive_summary.pdf` - executive summary
- `project_feedback_video_script.pdf` - video speaking script

## Important submission note
The project is an academic/internship analytics demonstration. The research paper is a project report and should not be described as "published" or "approved" unless it is actually approved/published by a journal or institution.
