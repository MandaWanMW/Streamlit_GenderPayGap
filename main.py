import pandas as pd
import plotly.express as px
import altair as alt
import streamlit as st
import numpy as np

# streamlit run main.py

# --------------- Read CSV --------------- #

df = pd.read_csv('data/data.csv')

# --------------- Sidebar - Filters --------------- #
st.sidebar.header("Please filter here for certain charts:")

# Filter Year
sel_year = st.sidebar.select_slider("Select a range of Year:",
                                    options=df["Year"].unique(),
                                    value=(df["Year"].iloc[0],
                                           df["Year"].iloc[-1]))

# Filter for Year Range
sel_year_range = df['Year'].between(*sel_year)

# Filter Country
sel_country = st.sidebar.selectbox("Select a Country:",
                                   options=df["Country"].unique())

# Create tuple for Sector (column names)
column_names = tuple(df.columns)

# Filter Sector
sel_sector = st.sidebar.selectbox("Select a Sector:", column_names[5:])

# Create df for year range
df_year = df.loc[sel_year_range]

# Create df for specific country and year range
df_year_country = df.loc[sel_year_range & (df["Country"] == sel_country)]

# --------------- Title --------------- #

st.title("Dashboard for Gender Pay Gap in Europe :bar_chart:")

# --------------- Gapminder Chart - GDP & Sector by Year --------------- #

gapminder = px.scatter(df_year, x='GDP', y=sel_sector, color='Country',
                       size='Urban_population', size_max=10,
                       title=f'Gapminder Chart by Year for {sel_sector} Sector',
                       animation_frame='Year', animation_group='Country',
                       hover_name='Country', range_y=[-50, 80],
                       labels={sel_sector: "Gender Pay Gap (%)"})

# --------------- Bar Chart - Gender Pay Gap by Sector --------------- #

# Select data in 2021
df_latest_data = df_year_country.loc[df_year_country['Year'] == df_year_country['Year'].max()]

# Select pay gaps columns, transpose the df, reset index, and add header,
df_latest_data_gap = df_latest_data.iloc[:, 5:].transpose().reset_index(drop=False
                                                                        ).set_axis(["Sector", "Pay_gap"],
                                                                                   axis=1, copy=False)

# Create chart
barchart_sector = alt.Chart(df_latest_data_gap,
                            title=f"Comparison of Pay Gap in Different Sectors in {sel_country}, "
                                  f"{df_year_country['Year'].max()}"
                  ).mark_bar().encode(
    x=alt.X("Pay_gap", axis=alt.Axis(title="Pay gap in the sector(%)")),
    y=alt.Y("Sector", sort='-x'),
        # The highlight will be set on the result of a conditional statement
        color=alt.condition(
        (alt.datum.Pay_gap == df_latest_data_gap['Pay_gap'].max()) |
        (alt.datum.Pay_gap == df_latest_data_gap['Pay_gap'].min()),
            alt.value('orange'),     # Highlight
            alt.value('steelblue')   # If it's not true it sets the bar steelblue.
        )
).properties(width=700)

# --------------- Line Chart - Gender Pay Gap - Moving Average (Predict) --------------- #

# Create a list for length of Moving Average
ma_length = [3, 5, 7]

# Create empty list for added MA columns
col_mas = []

# Create new columns for MA and calculate MA
for length in ma_length:
    column_ma = f"ma{length}"
    df_ma = df_year_country.copy()  # create a copy of the dataframe
    # Calculate MA
    df_ma[column_ma] = df_ma[sel_sector].rolling(window=length).mean()
    # Add to the empty list for MA columns
    col_mas.append(df_ma[[column_ma]])

# Combine the columns of Year, Sector, and MA
df_ma = pd.concat([df_year_country[['Year', sel_sector]]] + col_mas, axis=1)
# Concatenation should be done horizontally by columns

# Melt the dataframe
df_ma_melted = pd.melt(df_ma, id_vars=["Year"],
                       value_vars=([sel_sector] + [f"ma{length}" for length in ma_length]),
                       var_name="Variables", value_name="Values")

# Create MA linechart
linechart_ma = alt.Chart(df_ma_melted,
                         title=f"Trends in {sel_sector} Sector and Moving Averages (MA) in {sel_country}, "
                               f"{df_year_country['Year'].min()} - {df_year_country['Year'].max()}"
                         ).mark_line().encode(
    x=alt.X('Year', axis=alt.Axis(format='d')),
    y=alt.Y('Values', axis=alt.Axis(title="Gender Pay Gap (%)")),
    color='Variables'
).properties(width=700)

# --------------- Key Metrics --------------- #

st.markdown("**:blue[Key Metrics]**")

#Display KPI's Metrics
left_column, right_column = st.columns(2)



# --------------- Tab --------------- #

# Create Tabs
tab1, tab2, tab3 = st.tabs([
  "Gapminder Chart", "Comparison of Sector and Pay Gap", "Moving Average (MA)"
])

with tab1:
    st.plotly_chart(gapminder)
with tab2:
    st.altair_chart(barchart_sector, theme="streamlit", use_container_width=True)
with tab3:
    st.altair_chart(linechart_ma, theme="streamlit", use_container_width=True)