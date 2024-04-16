# 1. Importing Libraries:
    #The code imports various libraries such as time, base64, streamlit, pandas, geopandas, geopy, plotly_express, and numpy.
    #These libraries are necessary for performing geocoding, data manipulation, visualization, and web application development.
import time
import random
import string
import base64
import streamlit as st
import pandas as pd
import geopandas as gpd
import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import plotly_express as px
import numpy as np

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 2. Streamlit Application Setup:
    #The code uses Streamlit to create a web application. 
    #It sets the title of the application to “Geocoding Application in Python” and displays a markdown message instructing the user to upload a CSV file with address columns.
st.title('Geocoding Application: Convert Addresses into Coordinates')
st.markdown('Upload a CSV File containing your addresses.')
st.markdown('Addresses can be contained within a single column, or split by component into multiple columns (e.g., Street name & number | City | Postcode etc.)')

# 3. Function Definitions:
    #The code defines several functions used within the application:
        ##choose_geocode_column(df): Allows the user to select a column from a DataFrame (df) using a select box. It adds a new column named "geocode_col" to the DataFrame, containing the selected column's values.
        ##geocode(df): Performs geocoding on a DataFrame (df) using the Nominatim geocoder from the geopy library. It adds new columns to the DataFrame: "location" (containing geocoded location objects) and "point" (containing latitude, longitude, and altitude tuples). It also handles missing values in the "point" column and converts the "location" column to a string.
        ##display_map(df): Displays a scatter map using Plotly Express, based on the latitude and longitude columns of a DataFrame (df).
        ##download_csv(df): Converts a DataFrame (df) to a CSV format, encodes it in Base64, and generates a download link for the CSV file.
        ##display_results(gdf): Displays the geocoded results in the Streamlit application. It shows the first few rows of the DataFrame, plots the data on a map using display_map(), and provides a download link for the geocoded data.
        ##create_address_col(df): Allows the user to select address-related columns (street name, post code, city) from the sidebar. It concatenates the selected columns' values with appropriate separators and assigns the result to a new column named "geocode_col" in the DataFrame.
def choose_geocode_column(df):
    selection = st.selectbox("Select the column", df.columns.tolist())
    df["geocode_col"] = df[selection]
    return df

def geocode(df):
    letters = string.ascii_lowercase
    username = 'APPv212'
    locator = Nominatim(user_agent=username)
    geocode = RateLimiter(locator.geocode, min_delay_seconds=1)
    df["location"] = df["geocode_col"].apply(geocode)
    df["point"] = df["location"].apply(lambda loc: tuple(loc.point) if loc else None)
    
    # Handling missing values in the "point" column
    try:
        df[["latitude", "longitude", "altitude"]] = pd.DataFrame(
            df["point"].tolist(), index=df.index
        )
    except ValueError:
        # Handle missing values by assigning NaN or appropriate values
        df[["latitude", "longitude", "altitude"]] = np.nan

    df["location"] = df["location"].astype(str)  # Convert location column to string
    return df

@st.cache_data(persist=True)  # ,suppress_st_warning=True
def display_map(df):
    px.set_mapbox_access_token(
        "pk.eyJ1Ijoic2hha2Fzb20iLCJhIjoiY2plMWg1NGFpMXZ5NjJxbjhlM2ttN3AwbiJ9.RtGYHmreKiyBfHuElgYq_w"
    )
    fig = px.scatter_mapbox(df, lat="latitude", lon="longitude", zoom=10)
    return fig

def download_csv(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}">Download CSV File</a> (right-click and save link as &lt;some_name&gt;.csv)'
    return href

def display_results(gdf):
    with st.spinner("Geocoding Hold tight..."):
        time.sleep(5)
    st.success("Done!")
    st.write(gdf.head())
    st.plotly_chart(display_map(gdf))
    st.markdown(download_csv(gdf), unsafe_allow_html=True)

def create_address_col(df):
    st.sidebar.title("Select Address columns")
    st.sidebar.info(
        "You need to select address column (Street name and number), post code and City"
    )
    address_name = st.sidebar.selectbox("Select Address column", df.columns.tolist())
    post_code = st.sidebar.selectbox("Select Post Code Column", df.columns.tolist())
    city = st.sidebar.selectbox("Select the City Column", df.columns.tolist())
    country = st.sidebar.text_input("Write the country of the addresses")
    df["geocode_col"] = (
        df[address_name].astype(str)
        + ","
        + df[city]
        + ","
        + df[post_code]
        + ","
        + country
    )
    return df


# 4. Main Function:
    #The main() function handles the main execution of the Streamlit application:
        ##It allows the user to upload a CSV file using st.file_uploader().
        ##If a file is uploaded, it reads the CSV file into a DataFrame (df).
        ##It displays the uploaded DataFrame and its shape in the Streamlit application.
        ##It provides checkboxes for the user to select the address format: correctly formatted or not.
        ##If the address format is selected correctly, it calls choose_geocode_column() to choose the geocode column, performs geocoding using geocode(), and displays the geocoded results using display_results().
        ##If the address format is not correct, it calls create_address_col() to create the geocode column, performs geocoding using geocode(), and displays the geocoded results using display_results().
def main():
    file = st.file_uploader("Choose a file")
    if file is not None:
        file.seek(0)
        df = pd.read_csv(file, low_memory=False)
        with st.spinner("Reading CSV File..."):
            time.sleep(5)
            st.success("Done!")
        st.write(df.head())
        st.write(df.shape)

        cols = df.columns.tolist()

        st.subheader("Please select how your addresses are structured")
        st.info("Example correct address: 221 Baker Street, London, NW1 6XE")

        if st.checkbox("Select if your addresses are formatted like the example above"):
            st.subheader("From the dropdown, choose the column containing the addresses")
            df_address = choose_geocode_column(df)
            st.write(df_address["geocode_col"].head())
            geocoded_df = geocode(df_address)
            display_results(geocoded_df)

        if st.checkbox("Select if addresses are broken up into multiple columns (e.g. street, city, postcode, country)"):
            df_address = create_address_col(df)
            st.write(df_address["geocode_col"].head())
            geocoded_df = geocode(df_address)
            display_results(geocoded_df)

if __name__ == "__main__":
    main()