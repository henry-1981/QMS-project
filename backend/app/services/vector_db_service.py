import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.core.config import settings as app_settings


class VectorDBService:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=app_settings.CHROMA_PERSIST_DIRECTORY,
            settings=Settings(anonymized_telemetry=False)
        )
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=app_settings.GOOGLE_API_KEY
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " "]
        )
    
    def get_or_create_collection(self, name: str, metadata: Optional[Dict] = None):
        return self.client.get_or_create_collection(
            name=name,
            metadata=metadata or {}
        )
    
    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: List[Dict],
        ids: Optional[List[str]] = None
    ):
        collection = self.get_or_create_collection(collection_name)
        
        embeddings = self.embeddings.embed_documents(documents)
        
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]
        
        collection.add(
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
            ids=ids
        )
    
    def process_and_add_document(
        self,
        collection_name: str,
        text: str,
        metadata: Dict,
        doc_id_prefix: str = "chunk"
    ):
        chunks = self.text_splitter.split_text(text)
        
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            documents.append(chunk)
            chunk_metadata = metadata.copy()
            chunk_metadata['chunk_index'] = i
            metadatas.append(chunk_metadata)
            ids.append(f"{doc_id_prefix}_{i}")
        
        self.add_documents(collection_name, documents, metadatas, ids)
        
        return len(chunks)
    
    def search(
        self,
        collection_name: str,
        query: str,
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> Dict:
        collection = self.get_or_create_collection(collection_name)
        
        query_embedding = self.embeddings.embed_query(query)
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )
        
        return results
    
    def delete_documents(self, collection_name: str, ids: List[str]):
        collection = self.get_or_create_collection(collection_name)
        collection.delete(ids=ids)
    
    def delete_by_metadata(self, collection_name: str, where: Dict):
        collection = self.get_or_create_collection(collection_name)
        collection.delete(where=where)


vector_db_service = VectorDBService()
