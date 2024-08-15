import os
from pinecone import Pinecone, ServerlessSpec
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.objects import ObjectIndex
from llama_index.core import StorageContext
from llama_index.core.objects import SimpleToolNodeMapping
from llama_index.core import VectorStoreIndex
from typing import Optional, Any
from llama_index.core.schema import TextNode
from llama_index.embeddings.openai import OpenAIEmbedding

# Initialize Pinecone API key and client
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_CLIENT = Pinecone(PINECONE_API_KEY)


class PineconeClient:
    """
    Manages indices of tools and documents in Pinecone.
    """

    def __init__(self, collection_name):
        """
        Initialize the PineconeClient.

        :param collection_name: Name of the Pinecone collection.
        """
        self.collection_name = collection_name
        self._initialize_index()

        self.vector_store = PineconeVectorStore(
            pinecone_index=PINECONE_CLIENT.Index(collection_name))
        self.storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store)
        self.index = VectorStoreIndex.from_vector_store(
            embed_model = OpenAIEmbedding(model="text-embedding-3-small"),
            vector_store=self.vector_store)

    def _initialize_index(self):
        """Create the index if it does not exist."""
        if self.collection_name not in [i.get('name') for i in PINECONE_CLIENT.list_indexes()]:
            PINECONE_CLIENT.create_index(
                name=self.collection_name,
                dimension=1536,
                metric='cosine',
                spec=ServerlessSpec(cloud='aws', region='us-east-1')
            )

    def load_indices(self, objects: Optional[Any]):
        """Load function tools indices from the existing index."""
        return ObjectIndex.from_objects_and_index(objects, self.index)

    def upsert_indices(self, nodes: TextNode):
        """Upsert vector index and upload onto Pinecone."""

        self.vector_store.add(nodes)