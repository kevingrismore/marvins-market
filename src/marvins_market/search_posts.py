import asyncio

from prefect import flow, task
from pydantic import BaseModel, Field
from marvin import extract_async
from raggy.utils import create_openai_embeddings
from raggy.vectorstores.chroma import Chroma


class BlogRecommendation(BaseModel):
    title: str = Field(..., title="Title of the blog post")
    url: str = Field(..., title="URL of the blog post")
    description: str = Field(..., title="A very brief description of the blog post")


@flow
async def query_blogs(query: str, collection_name: str = "testing"):
    async with Chroma(
        collection_name=collection_name, client_type="persistent"
    ) as chroma:
        query_embeddings = await create_openai_embeddings(query)
        result = await chroma.query(
            query_embeddings=[query_embeddings],
            n_results=10,
            include=["metadatas", "distances", "documents"],
        )
        metadatas = result.get("metadatas")[0]
        distances = result.get("distances")[0]
        documents = result.get("documents")[0]

        recommendations = await extract_recommendations(documents, query)
        return recommendations


@task
async def extract_recommendations(documents, query):
    return await extract_async(
        data=("\n".join(documents)),
        target=BlogRecommendation,
        instructions=(
            "You are a product expert at Prefect. You will be provided with 10 excerpts from product marketing blog posts. Your goal is to help the marketing team to find blog posts that are relevant to the following query: "
            f"{query}"
            "Please provide the TOP 3 blog posts that are most relevant to the query."
        ),
    )
