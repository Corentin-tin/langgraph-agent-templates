"""Tools for document loading, processing, and retrieval."""

import os
import json
from typing import List, Any

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_cohere import CohereEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from shared.logging import get_logger

logger = get_logger(__name__)


def load_embeddings(provider: str = "openai", model: str = "text-embedding-3-small") -> Embeddings:
    """Load embedding model from specified provider."""
    logger.info("Loading embeddings", provider=provider, model=model)

    if provider == "openai":
        return OpenAIEmbeddings(model=model)
    elif provider == "cohere":
        return CohereEmbeddings(model=model)
    else:
        raise ValueError(f"Unsupported embedding provider: {provider}")


def load_vector_store(store_type: str, embeddings: Embeddings, **kwargs: Any) -> VectorStore:
    """Load vector store of specified type."""
    logger.info("Loading vector store", type=store_type)

    if store_type == "elasticsearch":
        from langchain_elasticsearch import ElasticsearchStore

        url = kwargs.get("url", os.getenv("ELASTICSEARCH_URL", "http://localhost:9200"))
        index_name = kwargs.get("index_name", "documents")

        return ElasticsearchStore(
            es_url=url,
            index_name=index_name,
            embedding=embeddings,
            es_cloud_id=os.getenv("ELASTICSEARCH_CLOUD_ID"),
            es_api_key=os.getenv("ELASTICSEARCH_API_KEY"),
        )

    elif store_type == "pinecone":
        from langchain_pinecone import PineconeVectorStore

        index_name = kwargs.get("index_name", os.getenv("PINECONE_INDEX"))
        if not index_name:
            raise ValueError("Pinecone index name required")

        return PineconeVectorStore(
            index_name=index_name,
            embedding=embeddings,
        )

    elif store_type == "mongodb":
        from langchain_mongodb import MongoDBAtlasVectorSearch

        uri = kwargs.get("uri", os.getenv("MONGODB_ATLAS_URI"))
        database = kwargs.get("database", os.getenv("MONGODB_DATABASE", "rag_database"))
        collection = kwargs.get("collection", os.getenv("MONGODB_COLLECTION", "documents"))
        index_name = kwargs.get("index_name", "vector_index")

        if not uri:
            raise ValueError("MongoDB Atlas URI required")

        return MongoDBAtlasVectorSearch(
            connection_string=uri,
            database_name=database,
            collection_name=collection,
            embedding=embeddings,
            index_name=index_name,
        )

    elif store_type == "faiss":
        from langchain_community.vectorstores import FAISS

        # Create empty FAISS index
        return FAISS.from_texts(
            texts=["Initial document"],  # Need at least one text to initialize
            embedding=embeddings,
        )

    else:
        raise ValueError(f"Unsupported vector store type: {store_type}")


async def load_sample_documents() -> List[Document]:
    """Load sample documents for indexing."""
    sample_docs_path = os.path.join(os.path.dirname(__file__), "../sample_docs.json")

    try:
        with open(sample_docs_path, "r") as f:
            data = json.load(f)

        documents = []
        for item in data:
            doc = Document(page_content=item["content"], metadata=item.get("metadata", {}))
            documents.append(doc)

        logger.info("Loaded sample documents", count=len(documents))
        return documents

    except FileNotFoundError:
        logger.warning("Sample documents file not found", path=sample_docs_path)
        return []
    except Exception as e:
        logger.error("Failed to load sample documents", error=str(e))
        return []


def split_documents(
    documents: List[Document], chunk_size: int = 1000, chunk_overlap: int = 200
) -> List[Document]:
    """Split documents into chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )

    chunks = splitter.split_documents(documents)
    logger.info(
        "Split documents into chunks", original_count=len(documents), chunk_count=len(chunks)
    )

    return chunks


async def retrieve_documents(vector_store: VectorStore, query: str, k: int = 10) -> List[Document]:
    """Retrieve relevant documents for a query."""
    try:
        docs = await vector_store.asimilarity_search(query, k=k)
        logger.info("Retrieved documents", query=query, count=len(docs))
        return docs
    except Exception as e:
        logger.error("Document retrieval failed", query=query, error=str(e))
        return []


def format_docs_xml(docs: List[Document]) -> str:
    """Format documents as XML for model consumption."""
    if not docs:
        return "<documents>\nNo documents found.\n</documents>"

    formatted = ["<documents>"]

    for i, doc in enumerate(docs):
        formatted.extend(
            [f'<document index="{i}">', f"<content>{doc.page_content}</content>", "<metadata>"]
        )

        for key, value in doc.metadata.items():
            formatted.append(f"<{key}>{value}</{key}>")

        formatted.extend(["</metadata>", "</document>"])

    formatted.append("</documents>")
    return "\n".join(formatted)
