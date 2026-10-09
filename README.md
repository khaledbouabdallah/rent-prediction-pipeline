# Rent Prediction Pipeline

An end-to-end data pipeline that predicts monthly rent for housing in France. We built every stage ourselves, from scraping the listings to a demo app: data collection, enrichment with nearby transport, cleaning, feature engineering, model comparison and serving.

University project, Université Paris Cité, 2023-2024. Team: Khaled Bouabdallah, Abir Idir, Asma Al Rifai and El Hadji Malick Sy. The full write-up is in [`Big_Data_project_DCI_S2.pdf`](Big_Data_project_DCI_S2.pdf).

## Pipeline

| Step | What it does | Where |
|---|---|---|
| Collection | Scrapy spiders collect rental listings from a French listings site, stored in PostgreSQL | `scraper/` |
| Enrichment | Google Places API finds transit stations within 2 km of each listing | `google_places_api/` |
| Preprocessing | Cleans the raw listings into a tabular dataset | `preprocessing/` |
| Feature engineering | Builds station features, including distance-weighted variants (linear, inverse, Gaussian, logarithmic) | `featureEngineering/` |
| Modelling | Compares classical regressors, XGBoost and an MLP, with Optuna hyperparameter search | `prediction/` |
| Demo | Streamlit app: enter a home's features and location, get a predicted rent with a SHAP explanation | `app.py` |

## Results

The dataset has 7,524 listings. Seven dataset variations were tested, with and without station features.

| Dataset variation | Best model | R² | MAE (€) |
|---|---|---|---|
| Listing features only | XGBoost | 0.784 | 102.3 |
| Station features, inverse-distance weighting | XGBoost | 0.791 | 101.5 |
| Station features, linear weighting | XGBoost | 0.789 | 101.3 |

XGBoost was the best model on every variation, ahead of Random Forest (R² about 0.77) and the MLP (R² about 0.56 at best). Station features gave a small improvement. All test results are in `prediction/results/`.

## Data is not included

The listings were scraped for this course project and are not redistributed here, and neither are the Google Places results or the trained models. Consequences:

- The notebooks are kept with their outputs, so the analysis and results can be read, but they cannot be re-run without the data.
- The Streamlit app needs the dataset and a trained model, so it does not run from this repository alone.
- The scraper no longer works: the site's structure has changed since 2024.

## Tech stack

Python, Scrapy, Splash, PostgreSQL, pandas, scikit-learn, XGBoost, Optuna, SHAP, Streamlit, Folium, Docker Compose.
