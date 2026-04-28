
# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# App title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# User input
name_on_order = st.text_input("Name on Smoothie:")
st.write('The name on Smoothie will be:', name_on_order)

# Snowflake connection (uses secrets.toml in Streamlit Cloud)
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit data
my_dataframe = session.table("smoothies.public.fruit_options") \
    .select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert to pandas
pd_df = my_dataframe.to_pandas()

# FIX: multiselect needs list, not dataframe
fruit_list = pd_df["FRUIT_NAME"].tolist()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

if ingredients_list:

    ingredients_string = ""

    for i in ingredients_list:
        ingredients_string += i + " "

        search_on = pd_df.loc[
            pd_df['FRUIT_NAME'] == i, 'SEARCH_ON'
        ].iloc[0]

        st.write('Search value for', i, 'is', search_on)

        st.subheader(i + " Nutrition Information")

        response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_on
        )

        st.dataframe(response.json(), use_container_width=True)

    st.write("Final ingredients:", ingredients_string)

    # Better SQL formatting
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")

