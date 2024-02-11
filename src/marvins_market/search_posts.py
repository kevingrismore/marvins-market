import asyncio

from prefect import flow
from raggy.utils import create_openai_embeddings
from raggy.vectorstores.chroma import Chroma


@flow
async def query_blogs(query: str, collection_name: str = "testing"):
    async with Chroma(
        collection_name=collection_name, client_type="persistent"
    ) as chroma:
        query_embeddings = await create_openai_embeddings(query)
        result = await chroma.query(
            query_embeddings=[query_embeddings],
            n_results=10,
            include=["metadatas", "distances"],
        )
        pages = result.get("metadatas")[0]
        distances = result.get("distances")[0]

        for metadata, distance in zip(pages, distances):
            print(metadata)
            print(f"distance: {1 - distance}")


if __name__ == "__main__":
    asyncio.run(query_blogs("is data engineering like mail or water?"))
