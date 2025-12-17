import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import os
from login import load_authenticator # calling function from login.py

st.set_page_config(page_title="My Single-Page App")

# 1. Create the authenticator
authenticator = load_authenticator()

# 2. Display the login form
#    The login form is titled "Login", and will appear in the main area ("main").
#    This returns (name, authentication_status, username).
try:
    authenticator.login()
except Exception as e:
    st.error(e)

# 3. Check login status

if st.session_state['authentication_status']:
    authenticator.logout("Logout","sidebar")
    #######################################################################################################################################
    # # Set page config to Main App
    # st.set_page_config(page_title="Main App")
    # st.title("Main App")

    # Set up the connection to the PostgreSQL database
    connection_string = os.getenv("DATABASE_URL")
    conn = create_engine(connection_string)

    # Title for the Streamlit app
    st.title('DCCA Price Monitoring App')

    # Load the data
    df = pd.read_sql("select * from analytics_data", con=conn)

    # --- Date Selection Section ---
    st.text('Please select the two dates you would like to compare:')

    # --- Let the user select two reference dates--- 
    # Create two columns for the date input fields
    col1, col2 = st.columns(2)

    # Let the user select two reference dates
    with col1:
        ref1 = st.date_input('Select Date 1', value=pd.to_datetime('2024-07-04'))

    with col2:
        ref2 = st.date_input('Select Date 2', value=pd.to_datetime('2024-08-22'))


    entry_date = [ref1, ref2]

    # Convert selected dates to datetime format
    #displayref1 = ref1.strftime("%B %Y")
    #displayref2 = ref2.strftime("%B %Y")

    # Convert selected dates to datetime format
    ref1 = pd.to_datetime(ref1)
    ref2 = pd.to_datetime(ref2)
    entry_date = [ref1, ref2]


    # Convert 'reference_date' to datetime in the DataFrame
    df['reference_date'] = pd.to_datetime(df['reference_date'].astype(str).str.strip(), format='%Y-%m-%d', errors='coerce')

    # Filter the data for the two selected dates
    df_filtered = df[df["reference_date"].isin(entry_date)]

    # --- Overall Average Price Comparison ---
    st.subheader(f'Overall Average Price Comparison between {ref1.strftime('%B %Y')} and {ref2.strftime('%B %Y')}')
    summary_type_overall = st.selectbox('Select Summary Type for Overall Average Price', ['Comparison', 'Change', 'Percentage Change'])

    avg_prices = df_filtered.groupby("reference_date")["price"].mean().reset_index()
    percentage_change = ((avg_prices['price'].iloc[1] - avg_prices['price'].iloc[0]) / avg_prices['price'].iloc[0]) * 100


    if summary_type_overall == 'Comparison':
        fig = px.bar(avg_prices, x="reference_date", y="price", text="price", title=f"Overall Average Price Comparison {ref1.strftime('%B %Y')} vs {ref2.strftime('%B %Y')}: {percentage_change:.2f}%",
                    labels={"price": "Average Price", "reference_date": "Reference Date"})
    elif summary_type_overall == 'Change':
        avg_prices['change'] = avg_prices['price'].diff().fillna(0)
        fig = px.bar(avg_prices, x="reference_date", y="change", text="change", title=f"Overall Price Change {ref1.strftime('%B %Y')} vs {ref2.strftime('%B %Y')}: {percentage_change:.2f}%",
                    labels={"change": "Price Change", "reference_date": "Reference Date"})
    else:
        avg_prices['percentage_change'] = avg_prices['price'].pct_change().fillna(0) * 100
        fig = px.bar(avg_prices, x="reference_date", y="percentage_change", text="percentage_change", title=f"Overall Price Percentage(%) Change {ref1.strftime('%B %Y')} vs {ref2.strftime('%B %Y')}: {percentage_change:.2f}%",
                    labels={"percentage_change": "Percentage Change", "reference_date": "Reference Date"})

    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    st.plotly_chart(fig)

    # --- Average Price Change by Category ---
    st.subheader('Average Price Change by Category')
    summary_type_category = st.selectbox('Select Summary Type for Price Change by Category', ['Comparison', 'Change', 'Percentage Change'])

    df_filtered_category = df_filtered.groupby(["category", "reference_date"])["price"].mean().unstack()

    if ref1 in df_filtered_category.columns and ref2 in df_filtered_category.columns:
        if summary_type_category == 'Comparison':
            df_filtered_category = df_filtered_category.reset_index()
            df_filtered_category = df_filtered_category.dropna(subset=[ref1, ref2])
            fig = px.bar(df_filtered_category, x="category", y=ref2, text=ref2, title=f"Average Price by Category (Comparison):  {ref1.strftime('%B %Y')} vs {ref2.strftime('%B %Y')}",
                        labels={ref2: "Average Price", "category": "Category"})
        elif summary_type_category == 'Change':
            df_filtered_category['change'] = (df_filtered_category[ref2] - df_filtered_category[ref1]).fillna(0)
            df_filtered_category = df_filtered_category.reset_index()
            fig = px.bar(df_filtered_category, x="category", y="change", text="change", title=f"Price Change by Category:  {ref1.strftime('%B %Y')} vs {ref2.strftime('%B %Y')}",
                        labels={"change": "Price Change", "category": "Category"})
        else:
            df_filtered_category['percentage_change'] = ((df_filtered_category[ref2] - df_filtered_category[ref1]) / df_filtered_category[ref1]) * 100
            df_filtered_category = df_filtered_category.reset_index()
            df_filtered_category = df_filtered_category.dropna(subset=['percentage_change'])
            fig = px.bar(df_filtered_category, x="category", y="percentage_change", text="percentage_change", 
                        title=f"Percentage Price Change(%) by Category: {ref1.strftime('%B %Y')} vs {ref2.strftime('%B %Y')}", labels={"percentage_change": "Percentage Change", "category": "Category"})
    else:
        st.warning(f"One or both of the reference dates ({ref1}, {ref2}) are missing in the dataset for this category.")
        fig = None  # Avoid rendering a broken chart if data is missing

    if fig:
        fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        st.plotly_chart(fig)


    # --- Average Price Change by Commodity (Subcategory) (within a selected category) ---
    #st.subheader('Average Price Change by Subcategory')
    # Create two columns for the date selector fields
    col3, col4 = st.columns(2)
    with col3:
        # User selects a category
        selected_category = st.selectbox('Select a Category', df['category'].unique())

    with col4:
        # User selects summary type
        summary_type_subcategory = st.selectbox('Select Summary Type', ['Comparison', 'Change', 'Percentage Change'])

    # Filter by selected category and dates
    df_filtered_subcategory = df[(df["reference_date"].isin(entry_date)) & (df["category"] == selected_category)]
    df_filtered_subcategory_grouped = df_filtered_subcategory.groupby(["subcategory", "reference_date"])["price"].mean().unstack()

    # Generate chart based on the selected summary type
    if ref1 in df_filtered_subcategory_grouped.columns and ref2 in df_filtered_subcategory_grouped.columns:
        if summary_type_subcategory == 'Comparison':
            df_filtered_subcategory_grouped = df_filtered_subcategory_grouped.reset_index()
            fig = px.bar(df_filtered_subcategory_grouped, x="subcategory", y=ref2, text=ref2, title=f"Average Price by Commodity ({selected_category}): {ref1.strftime('%B %Y')} vs {ref2.strftime('%B %Y')}",
                        labels={ref2: "Average Price", "subcategory": "Subcategory"})
        elif summary_type_subcategory == 'Change':
            df_filtered_subcategory_grouped['change'] = (df_filtered_subcategory_grouped[ref2] - df_filtered_subcategory_grouped[ref1]).fillna(0)
            df_filtered_subcategory_grouped = df_filtered_subcategory_grouped.reset_index()
            fig = px.bar(df_filtered_subcategory_grouped, x="subcategory", y="change", text="change", title=f"Price Change by Commodity ({selected_category}): {ref1.strftime('%B %Y')} vs {ref2.strftime('%B %Y')}",
                        labels={"change": "Price Change", "subcategory": "Subcategory"})
        else:
            df_filtered_subcategory_grouped['percentage_change'] = ((df_filtered_subcategory_grouped[ref2] - df_filtered_subcategory_grouped[ref1]) / df_filtered_subcategory_grouped[ref1]) * 100
            df_filtered_subcategory_grouped = df_filtered_subcategory_grouped.reset_index()
            df_filtered_subcategory_grouped = df_filtered_subcategory_grouped.dropna(subset=['percentage_change'])
            fig = px.bar(df_filtered_subcategory_grouped, x="subcategory", y="percentage_change", text="percentage_change", 
                        title=f"Percentage Price Change (%) by Commodity ({selected_category}): {ref1.strftime('%B %Y')} vs {ref2.strftime('%B %Y')}", 
                        labels={"percentage_change": "Percentage Change", "subcategory": "Subcategory"})
    else:
        st.warning(f"One or both of the reference dates ({ref1}, {ref2}) are missing in the dataset for this subcategory.")
        fig = None

    # Display the chart
    if fig:
        fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        st.plotly_chart(fig)

    # --- Average Price Change by Commodity section ---
    # Create two columns for the date input fields
    col5, col6 = st.columns(2)

    with col5:
        selected_subcategory = st.selectbox('Select a Commodity ', df['subcategory'].unique())
    with col6:
        summary_type_product = st.selectbox('Select Summary Type for Commodity', ['Comparison', 'Change', 'Percentage Change'])



    df_filtered_product = df[(df["reference_date"].isin(entry_date)) & (df["subcategory"] == selected_subcategory)]

    df_filtered_product_grouped = df_filtered_product.groupby(["product_name", "reference_date"])["price"].mean().unstack()

    # --- Average Price Change by Products Chart ---

    # --- Average Price Change by Products(Item) Chart ---
    if ref1 in df_filtered_product_grouped.columns and ref2 in df_filtered_product_grouped.columns:
        if summary_type_product == 'Comparison':
            df_filtered_product_grouped = df_filtered_product_grouped.reset_index()
            fig = px.bar(df_filtered_product_grouped, x="product_name", y=ref2, text=ref2, title=f"Average Price by Item in {selected_category} (Comparison): {ref1.strftime('%B %Y')} vs {ref2.strftime('%B %Y')}",
                        labels={ref2: "Average Price", "product_name": "Product"})
        elif summary_type_product == 'Change':
            df_filtered_product_grouped['change'] = (df_filtered_product_grouped[ref2] - df_filtered_product_grouped[ref1]).fillna(0)
            df_filtered_product_grouped = df_filtered_product_grouped.reset_index()
            fig = px.bar(df_filtered_product_grouped, x="product_name", y="change", text="change", title=f"Price Change by Item in {selected_category}: {ref1.strftime('%B %Y')} vs {ref2.strftime('%B %Y')}",
                        labels={"change": "Price Change", "product_name": "Product"})
        else:
            df_filtered_product_grouped['percentage_change'] = ((df_filtered_product_grouped[ref2] - df_filtered_product_grouped[ref1]) / df_filtered_product_grouped[ref1]) * 100
            df_filtered_product_grouped = df_filtered_product_grouped.reset_index()
            df_filtered_product_grouped = df_filtered_product_grouped.dropna(subset=['percentage_change'])
            fig = px.bar(df_filtered_product_grouped, x="product_name", y="percentage_change", text="percentage_change", 
                        title=f"Percentage Price Change by Item in {selected_category}: {ref1.strftime('%B %Y')} vs {ref2.strftime('%B %Y')}", 
                        labels={"percentage_change": "Percentage Change", "product_name": "Product"})
    else:
        st.warning(f"One or both of the reference dates ({ref1}, {ref2}) are missing in the dataset for this product.")
        fig = None

    if fig:
        fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        st.plotly_chart(fig)

    # --- Average Price by Supermarket ---
    summary_type_vendor = st.selectbox('Select Summary Type for Average Price by Supermarket', ['Comparison', 'Change', 'Percentage Change'])

    avg_prices_by_vendor = df_filtered.groupby(["vendor_group_name", "reference_date"])["price"].mean().reset_index()

    if ref1 in avg_prices_by_vendor['reference_date'].values and ref2 in avg_prices_by_vendor['reference_date'].values:
        if summary_type_vendor == 'Comparison':
            fig = px.bar(avg_prices_by_vendor, x="vendor_group_name", y="price", color="reference_date", barmode="group", text="price",
                        title=f"Average Price by Supermarket: {ref1.strftime('%B %Y')} vs {ref2.strftime('%B %Y')}", labels={"price": "Average Price", "vendor_group_name": "Supermarket", "reference_date": "Entry Date"})
        elif summary_type_vendor == 'Change':
            avg_prices_by_vendor = avg_prices_by_vendor.pivot(index='vendor_group_name', columns='reference_date', values='price').reset_index()
            avg_prices_by_vendor['change'] = (avg_prices_by_vendor[ref2] - avg_prices_by_vendor[ref1]).fillna(0)
            fig = px.bar(avg_prices_by_vendor, x="vendor_group_name", y="change", text="change", title=f"Price Change by Supermarket: {ref1.strftime('%B %Y')} vs {ref2.strftime('%B %Y')}",
                        labels={"change": "Price Change", "vendor_group_name": "Supermarket"})
        else:
            avg_prices_by_vendor = avg_prices_by_vendor.pivot(index='vendor_group_name', columns='reference_date', values='price').reset_index()
            avg_prices_by_vendor['percentage_change'] = ((avg_prices_by_vendor[ref2] - avg_prices_by_vendor[ref1]) / avg_prices_by_vendor[ref1]) * 100
            fig = px.bar(avg_prices_by_vendor, x="vendor_group_name", y="percentage_change", text="percentage_change", 
                        title=f"Percentage Price Change by Supermarket: {ref1.strftime('%B %Y')} vs {ref2.strftime('%B %Y')}", labels={"percentage_change": "Percentage Change", "vendor_group_name": "Supermarket"})
    else:
        st.warning(f"One or both of the reference dates ({ref1}, {ref2}) are missing in the dataset for these supermarkets.")
        fig = None

    if fig:
        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        st.plotly_chart(fig)

    # --- Average Price by Category for Selected Supermarket ---
    st.subheader('Average Price by Category for Selected Supermarket')

    ##Add columns here then remove this comment
    # Create two columns for the date input fields
    col7, col8 = st.columns(2)

    with col7:
        selected_vendor = st.selectbox('Select a Supermarket', df['vendor_group_name'].unique())
    with col8:
        summary_type_vendor_category = st.selectbox('Select Summary Type for Price by Category for Supermarket', ['Comparison', 'Change', 'Percentage Change'])

    df_filtered_vendor = df[(df["reference_date"].isin(entry_date)) & (df["vendor_group_name"] == selected_vendor)]
    avg_prices_by_category_vendor = df_filtered_vendor.groupby(["category", "reference_date"])["price"].mean().reset_index()

    if ref1 in avg_prices_by_category_vendor['reference_date'].values and ref2 in avg_prices_by_category_vendor['reference_date'].values:
        if summary_type_vendor_category == 'Comparison':
            fig = px.bar(avg_prices_by_category_vendor, x="category", y="price", color="reference_date", barmode="group", text="price",
                        title=f"Average Price by Category for {selected_vendor}: {ref1.strftime('%B %Y')} vs {ref2.strftime('%B %Y')}", labels={"price": "Average Price", "category": "Category", "reference_date": "Entry Date"})
        elif summary_type_vendor_category == 'Change':
            avg_prices_by_category_vendor = avg_prices_by_category_vendor.pivot(index='category', columns='reference_date', values='price').reset_index()
            avg_prices_by_category_vendor['change'] = (avg_prices_by_category_vendor[ref2] - avg_prices_by_category_vendor[ref1]).fillna(0)
            fig = px.bar(avg_prices_by_category_vendor, x="category", y="change", text="change", title=f"Price Change by Category for {selected_vendor}: {ref1.strftime('%B %Y')} vs {ref2.strftime('%B %Y')}",
                        labels={"change": "Price Change", "category": "Category"})
        else:
            avg_prices_by_category_vendor = avg_prices_by_category_vendor.pivot(index='category', columns='reference_date', values='price').reset_index()
            avg_prices_by_category_vendor['percentage_change'] = ((avg_prices_by_category_vendor[ref2] - avg_prices_by_category_vendor[ref1]) / avg_prices_by_category_vendor[ref1]) * 100
            fig = px.bar(avg_prices_by_category_vendor, x="category", y="percentage_change", text="percentage_change", 
                        title=f"Percentage Price Change by Category for {selected_vendor}: {ref1.strftime('%B %Y')} vs {ref2.strftime('%B %Y')}", 
                        labels={"percentage_change": "Percentage Change", "category": "Category"})
    else:
        st.warning(f"One or both of the reference dates ({ref1}, {ref2}) are missing in the dataset for this supermarket.")
        fig = None

    if fig:
        fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        st.plotly_chart(fig)

#######################################################################################################################################

elif st.session_state['authentication_status'] is False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] is None:
    st.warning('Please enter your username and password')
