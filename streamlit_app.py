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

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit data
my_dataframe = session.table("smoothies.public.fruit_options") \
    .select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert to pandas
pd_df = my_dataframe.to_pandas()

# Multiselect ingredient picker
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

        st.subheader(i + " Nutrition Information")
        response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_on
        )

        if response.status_code == 200:
            st.dataframe(response.json(), use_container_width=True)
        else:
            st.warning(f"Could not fetch nutrition info for {i}")

    st.write("Final ingredients:", ingredients_string)

    # SQL insert
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string.strip()}', '{name_on_order.replace("'", "''")}')
    """

    if st.button("Submit Order"):
        if not name_on_order:
            st.error("Please enter a name for your order!")
        else:
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
