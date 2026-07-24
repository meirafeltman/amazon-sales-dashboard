import pandas as pd
import streamlit as st
import plotly.express as px

# Page setup
st.set_page_config(page_title="Amazon Sales Dashboard", layout="wide")

st.title("Amazon Sales Data Dashboard")
st.write(
    "This dashboard explores the Amazon Sales Dataset (Kaggle) to look at "
    "product pricing, discounts, ratings, and categories. Use it to get a "
    "quick read on which categories dominate the catalog, how pricing and "
    "discounting behave, and whether higher ratings track with price."
)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("data/raw/amazon.csv")
    return df

raw_df = load_data()


# Cleaning
# discounted_price / actual_price: text like "₹1,099" -> float
# discount_percentage: text like "64%" -> float
# rating: mostly numeric strings, but at least one row has a stray "|"
#   placeholder instead of a number. We coerce to numeric and drop the
#   rows that fail (they're not usable for a numeric ratings analysis).
# rating_count: text with commas, and a couple of missing values.
#   We coerce to numeric and drop rows we can't use for count-based charts.

@st.cache_data
def clean_data(df):
    df = df.copy()

    for col in ["discounted_price", "actual_price"]:
        df[col] = (
            df[col].astype(str)
            .str.replace("₹", "", regex=False)
            .str.replace(",", "", regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["discount_percentage"] = (
        df["discount_percentage"].astype(str).str.replace("%", "", regex=False)
    )
    df["discount_percentage"] = pd.to_numeric(df["discount_percentage"], errors="coerce")

    # "rating" has at least one non-numeric placeholder ("|"). Coercing
    # with errors="coerce" turns that into NaN instead of crashing.
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

    df["rating_count"] = df["rating_count"].astype(str).str.replace(",", "", regex=False)
    df["rating_count"] = pd.to_numeric(df["rating_count"], errors="coerce")

    # Use only the top-level category (before the first "|") so the
    # category charts are readable instead of showing 200+ nested paths.
    df["main_category"] = df["category"].astype(str).str.split("|").str[0]

    before = len(df)
    df = df.dropna(subset=["discounted_price", "actual_price", "rating", "rating_count"])
    after = len(df)
    dropped = before - after

    return df, dropped

df, rows_dropped = clean_data(raw_df)

# Preview

with st.expander("Preview raw dataset"):
    st.dataframe(raw_df.head(20))
    st.caption(
        f"Loaded {len(raw_df):,} rows. After cleaning price, rating, and "
        f"review-count fields, {rows_dropped:,} rows with unusable values "
        f"were dropped, leaving {len(df):,} rows for the analysis below."
    )

# Summary metrics
st.header("Summary metrics")

col1, col2, col3 = st.columns(3)
col1.metric("Products analyzed", f"{len(df):,}")
col2.metric("Average rating", f"{df['rating'].mean():.2f} / 5")
col3.metric("Average discount", f"{df['discount_percentage'].mean():.0f}%")


# Chart 1: Which categories have the most products?
st.header("Which categories have the most products?")

category_counts = (
    df["main_category"].value_counts().head(10).reset_index()
)
category_counts.columns = ["main_category", "product_count"]

fig1 = px.bar(
    category_counts,
    x="product_count",
    y="main_category",
    orientation="h",
    labels={"product_count": "Number of products", "main_category": "Category"},
)
fig1.update_layout(yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig1, use_container_width=True)

st.write(
    f"**Takeaway:** {category_counts.iloc[0]['main_category']} is the largest "
    f"category in the dataset by product count. The catalog is fairly "
    f"concentrated in its top few categories rather than spread evenly "
    f"across many."
)

# Chart 2: Which categories have the highest average ratings?
st.header("Which categories have the highest average ratings?")

min_products = st.slider(
    "Minimum products in category (to avoid tiny, noisy averages)", 1, 30, 5
)

category_ratings = (
    df.groupby("main_category")
    .agg(avg_rating=("rating", "mean"), product_count=("rating", "size"))
    .query("product_count >= @min_products")
    .sort_values("avg_rating", ascending=False)
    .head(10)
    .reset_index()
)

fig2 = px.bar(
    category_ratings,
    x="avg_rating",
    y="main_category",
    orientation="h",
    labels={"avg_rating": "Average rating", "main_category": "Category"},
)
fig2.update_layout(yaxis={"categoryorder": "total ascending"}, xaxis_range=[0, 5])
st.plotly_chart(fig2, use_container_width=True)

st.write(
    "**Takeaway:** Average ratings across categories are fairly close together "
    "(most sit in a narrow band), which suggests rating alone isn't a strong "
    "way to tell categories apart in this dataset."
)

# Chart 3: Actual price vs discounted price / rating
st.header("How does price relate to rating?")

fig3 = px.scatter(
    df,
    x="discounted_price",
    y="rating",
    size="rating_count",
    color="main_category",
    hover_data=["product_name"],
    labels={"discounted_price": "Discounted price (₹)", "rating": "Rating"},
    log_x=True,
)
st.plotly_chart(fig3, use_container_width=True)

st.write(
    "**Takeaway:** There's no strong visual trend between price and rating, "
    "points across almost every price range sit at similar rating levels. "
    "Higher price does not clearly buy a higher rating in this dataset."
)

# Chart 4: Biggest discounts
st.header("Which products have the biggest discounts?")

top_discounts = (
    df.sort_values("discount_percentage", ascending=False)
    .head(10)[["product_name", "main_category", "actual_price", "discounted_price", "discount_percentage"]]
)
st.dataframe(top_discounts, use_container_width=True)

st.write(
    "**Takeaway:** The steepest discounts cluster in a handful of categories "
    "rather than being spread evenly, worth checking against actual price "
    "so a large percentage discount isn't misread on a very cheap item."
)
