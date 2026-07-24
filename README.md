# Amazon Sales Data Dashboard

A Streamlit dashboard exploring the [Amazon Sales Dataset](https://www.kaggle.com/datasets/karkavelrajaj/amazon-sales-dataset) from Kaggle — products, prices, discounts, ratings, and categories.

## Setup

This project uses [uv](https://docs.astral.sh/uv/) for Python and package management.

1. Clone this repo and open it in a Codespace (or locally).
2. Install dependencies:
   ```
   uv sync
   ```
3. Download `amazon.csv` from the [Kaggle dataset page](https://www.kaggle.com/datasets/karkavelrajaj/amazon-sales-dataset) (free Kaggle account required) and place it at:
   ```
   data/raw/amazon.csv
   ```
   This file is not committed to the repo (see `.gitignore`).
4. Run the dashboard:
   ```
   uv run streamlit run app.py
   ```
5. If running in a Codespace, open the forwarded port when prompted (or check the "Ports" tab) to view the dashboard in your browser.

## Data cleaning

The raw CSV has several fields that don't load cleanly as numbers:

- **`discounted_price` / `actual_price`** — stored as text with a ₹ symbol and thousands commas (e.g. `"₹1,099"`). Stripped both characters and cast to float.
- **`discount_percentage`** — stored as a percentage string (e.g. `"64%"`). Stripped the `%` and cast to float.
- **`rating`** — mostly numeric strings, but at least one row has a non-numeric placeholder value. Converted with `errors="coerce"` so bad values become `NaN` instead of crashing the load, then dropped those rows for the ratings analysis.
- **`rating_count`** — text with thousands commas and a couple of missing values. Stripped commas, cast to float, and dropped rows that couldn't convert.

Rows that couldn't be cleanly converted on any of these fields were dropped rather than imputed, since guessing a price or rating would distort the summary metrics. This dropped 3 rows out of 1,465.

- **`category`** is a pipe-delimited path (e.g. `Computers&Accessories|Accessories&Peripherals|...`). The dashboard uses only the first segment (`main_category`) so category charts stay readable.

## Files

- `app.py` — the Streamlit dashboard
- `data/raw/amazon.csv` — the dataset (not committed — see above)
- `screenshots/` — dashboard screenshots for the writeup
- `AI_USE.md` — log of AI tool usage during this project
