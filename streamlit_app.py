# Import python packages
import streamlit as st
import snowflake.connector
import pandas as pd
import requests

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")

# Connect to Snowflake using secrets
conn = snowflake.connector.connect(
    user=st.secrets["snowflake"]["user"],
    password=st.secrets["snowflake"]["password"],
    account=st.secrets["snowflake"]["account"],
    warehouse=st.secrets["snowflake"]["warehouse"],
    database=st.secrets["snowflake"]["database"],
    schema=st.secrets["snowflake"]["schema"],
    role=st.secrets["snowflake"]["role"]
)

# Load fruit data
query = "SELECT FRUIT_NAME, SEARCH_ON FROM smoothies.public.fruit_options"
df = pd.read_sql(query, conn)

fruit_list = df["FRUIT_NAME"].tolist()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ""

    for i in ingredients_list:
        ingredients_string += i + " "

        search_on = df.loc[df['FRUIT_NAME'] == i, 'SEARCH_ON'].iloc[0]

        st.subheader(i + " Nutrition Information")

        response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_on
        )

        st.dataframe(response.json(), use_container_width=True)

    if st.button("Submit Order"):
        insert_query = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
        """

        cursor = conn.cursor()
        cursor.execute(insert_query)
        st.success("Order placed!", icon="✅")
