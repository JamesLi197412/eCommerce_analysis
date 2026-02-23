# End-to-End E-Commerce Analytics (Olist)

## Project Summary
This project analyzes the Olist Brazilian e-commerce dataset from Kaggle and builds a full analytics workflow:
- SQL analysis for business KPIs and trend tracking
- Python analytics for commercial, delivery, and customer behavior insights
- NLP on review text (sentiment classification + topic modeling)
- Dashboard outputs in Tableau and Power BI

The goal is to translate raw marketplace data into actionable insights for growth, customer retention, and operations.

## Dataset
- Source: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
- Tables used: customers, orders, order_items, payments, reviews, products, sellers, geolocation, category translation
- Scale: ~1.56M rows across raw CSV files

## Business Questions Covered
1. How do sales vary by state/city, product category, and time?
2. What is customer buying frequency and estimated customer lifetime value (CLV)?
3. How well does delivery execution perform vs estimated dates?
4. What themes and sentiment appear in customer reviews?
5. Which product categories are bought together?

## Tech Stack
- Python 3.9
- pandas, NumPy, matplotlib, seaborn
- scikit-learn, XGBoost (with fallback model support)
- gensim, pyLDAvis
- networkx, mlxtend
- MySQL, AWS S3 (data transfer utilities)
- Tableau and Power BI

## Project Structure
- `/Users/jamesli/Desktop/ecommerce/analysis` - business analysis modules
- `/Users/jamesli/Desktop/ecommerce/model` - ML/NLP model classes
- `/Users/jamesli/Desktop/ecommerce/src` - data access and transfer utilities
- `/Users/jamesli/Desktop/ecommerce/sql practice` - SQL schema and analysis queries
- `/Users/jamesli/Desktop/ecommerce/output` - generated model/visual outputs
- `/Users/jamesli/Desktop/ecommerce/dashboard works` - Tableau/Power BI files

## Setup
```bash
python3.9 -m pip install -r requirements.txt
```

## Run
Full pipeline:
```bash
MPLCONFIGDIR=/tmp/matplotlib python3.9 main.py
```

Quick smoke run (recommended for validation):
```bash
MPLCONFIGDIR=/tmp/matplotlib python3.9 main.py --quick-rows 500 --skip-exploration
```

Optional flags:
- `--skip-delivery`
- `--skip-review`
- `--skip-network`
- `--skip-exploration`
- `--quick-rows N`

## Outputs
Examples are saved under:
- `/Users/jamesli/Desktop/ecommerce/output/visualisations/commercial`
- `/Users/jamesli/Desktop/ecommerce/output/visualisations/delivery`
- `/Users/jamesli/Desktop/ecommerce/output/visualisations/network`
- `/Users/jamesli/Desktop/ecommerce/output/model_evaluation`

## Notes on Robustness
The pipeline now includes graceful fallbacks when optional packages are unavailable:
- `xgboost` missing -> uses `RandomForestRegressor` fallback for delivery prediction
- `lifetimes` missing -> uses simplified CLV proxy
- `mlxtend` missing -> uses pairwise association-rule fallback
- `squarify` missing -> uses bar-chart fallback for category charting

This keeps the project runnable in constrained environments while preserving analysis flow.
