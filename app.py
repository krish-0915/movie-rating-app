import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from data_loader import load_cleaned_data, genre_decade_matrix, director_consistency, top_movies

sns.set_style("darkgrid")

# in app.py, change:
from data_loader import load_movie_data
...
def get_data():
    return load_movie_data(min_votes=1000)

# to:
from data_loader import load_cleaned_data
...
def get_data():
    return load_cleaned_data()

# Step 5.1 — Page setup
st.set_page_config(page_title="Movie Ratings Dashboard", layout="wide")
st.title("🎬 Movie Ratings Analysis Dashboard")

# Step 5.2 + 5.3 — Load data (cached)
@st.cache_data
def get_data():
    return load_cleaned_data()

df, df_exploded = get_data()

# Step 5.4 — Sidebar filter: decade range
st.sidebar.header("Filters")

min_decade = int(df['decade'].min())
max_decade = int(df['decade'].max())
decade_range = st.sidebar.slider(
    "Decade range",
    min_value=min_decade,
    max_value=max_decade,
    value=(min_decade, max_decade),
    step=10
)

# Step 5.5 — Sidebar filter: genre selector
all_genres = sorted(df_exploded['genres'].unique())
selected_genres = st.sidebar.multiselect(
    "Genres",
    options=all_genres,
    default=all_genres
)

# Step 5.6 — Sidebar filter: minimum votes
min_votes_filter = st.sidebar.slider(
    "Minimum number of votes",
    min_value=1000,
    max_value=50000,
    value=1000,
    step=1000
)

# Step 5.7 — Apply filters
filtered_df = df[
    (df['decade'] >= decade_range[0]) &
    (df['decade'] <= decade_range[1]) &
    (df['numVotes'] >= min_votes_filter)
]

filtered_exploded = df_exploded[
    (df_exploded['decade'] >= decade_range[0]) &
    (df_exploded['decade'] <= decade_range[1]) &
    (df_exploded['numVotes'] >= min_votes_filter) &
    (df_exploded['genres'].isin(selected_genres))
]

# Step 5.8 — Empty-result guard
if filtered_df.empty:
    st.warning("No movies match the current filters. Try widening your selection.")
    st.stop()

# Step 6.2 — Rating Distribution by Genre (violin plot)
st.header("Rating Distribution by Genre")

fig, ax = plt.subplots(figsize=(12, 5))
sns.violinplot(data=filtered_exploded, x='genres', y='averageRating', ax=ax)
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
ax.set_xlabel("Genre")
ax.set_ylabel("Average Rating")
st.pyplot(fig)

# Step 6.4 — Average Rating by Genre and Decade (heatmap)
st.header("Average Rating by Genre and Decade")

matrix = genre_decade_matrix(filtered_exploded)

fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(matrix, annot=True, fmt=".1f", cmap="YlOrRd", ax=ax, cbar_kws={'label': 'Avg Rating'})
ax.set_xlabel("Decade")
ax.set_ylabel("Genre")
st.pyplot(fig)

# Step 6.5 — Runtime vs Rating (scatter)
st.header("Runtime vs Rating")

fig, ax = plt.subplots(figsize=(10, 5))
sns.scatterplot(data=filtered_df, x='runtimeMinutes', y='averageRating', alpha=0.2, ax=ax)
sns.regplot(data=filtered_df, x='runtimeMinutes', y='averageRating', scatter=False, color='red', ax=ax)
ax.set_xlabel("Runtime (minutes)")
ax.set_ylabel("Average Rating")
st.pyplot(fig)

corr = filtered_df['runtimeMinutes'].corr(filtered_df['averageRating'])
st.caption(f"Correlation coefficient: {corr:.3f}")

# Step 6.6 — Director Consistency (bar chart)
st.header("Director Consistency")

stats = director_consistency(filtered_df, min_films=5)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Most Consistent")
    most_consistent = stats.sort_values('std').head(10)
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(x=most_consistent['std'], y=most_consistent.index, ax=ax, color='steelblue')
    ax.set_xlabel("Rating Std Dev")
    st.pyplot(fig)

with col2:
    st.subheader("Most Polarizing")
    most_polarizing = stats.sort_values('std', ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(x=most_polarizing['std'], y=most_polarizing.index, ax=ax, color='indianred')
    ax.set_xlabel("Rating Std Dev")
    st.pyplot(fig)

# Step 6.7 — Top Rated Movies (table)
st.header("Top Rated Movies")

min_votes_top = st.slider("Minimum votes for this list", 1000, 50000, 5000, step=1000)
top = top_movies(filtered_df, min_votes=min_votes_top, n=20)
st.dataframe(top, width='stretch')

# Step 5.10 — Row count in sidebar
st.sidebar.markdown(f"**{len(filtered_df):,} movies match current filters**")