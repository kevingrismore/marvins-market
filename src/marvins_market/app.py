import streamlit as st
import streamlit_pydantic as sp

from search_posts import query_blogs
from search_posts import BlogRecommendation

import asyncio


def search(query: str):
    blogs: list[BlogRecommendation] = asyncio.run(query_blogs(query=query))
    sp.pydantic_output(blogs)


query = st.text_input(label="Enter a query to search for blog posts")
button = st.button("Search", on_click=search, args=[query])
