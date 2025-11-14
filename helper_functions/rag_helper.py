import os
import json
from typing import List, Dict
import faiss
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from pypdf import PdfReader
import pickle


class RAGSystem:
    """RAG System for credit card knowledge base and uploaded documents"""
    
    def __init__(self, openai_api_key: str):
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.index = None
        self.documents = []
        self.vector_store_path = "data/faiss_index"
        self.docs_path = "data/documents.pkl"
        
    def load_credit_card_kb(self, json_path: str = "data/credit-card-kb.json") -> List[Document]:
        """Load credit card knowledge base from JSON Lines file"""
        documents = []
        
        try:
            with open(json_path, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    
                    # Format the data into readable text
                    if 'type' in data:  # Entity
                        text = self._format_entity(data)
                    elif 'source' in data:  # Relationship
                        text = self._format_relationship(data)
                    else:
                        continue
                    
                    doc = Document(
                        page_content=text,
                        metadata={"source": "credit_card_kb", "data": json.dumps(data)}
                    )
                    documents.append(doc)
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
        
        return documents
    
    def _format_entity(self, data: Dict) -> str:
        """Format entity data into readable text"""
        entity_type = data.get('type', 'Unknown')
        entity_id = data.get('id', '')
        props = data.get('properties', {})
        
        text = f"{entity_type}: {entity_id}\n"
        for key, value in props.items():
            text += f"  {key}: {value}\n"
        
        return text
    
    def _format_relationship(self, data: Dict) -> str:
        """Format relationship data into readable text"""
        source = data.get('source', '')
        target = data.get('target', '')
        relation = data.get('relation', '')
        props = data.get('properties', {})
        
        text = f"Relationship: {source} --[{relation}]--> {target}\n"
        for key, value in props.items():
            text += f"  {key}: {value}\n"
        
        return text
    
    def process_pdf(self, pdf_file) -> List[Document]:
        """Process uploaded PDF file"""
        documents = []
        
        try:
            pdf_reader = PdfReader(pdf_file)
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                if text.strip():
                    doc = Document(
                        page_content=text,
                        metadata={"source": pdf_file.name, "page": page_num + 1}
                    )
                    documents.append(doc)
        except Exception as e:
            print(f"Error processing PDF: {e}")
        
        return documents
    
    def build_vector_store(self, documents: List[Document]):
        """Build FAISS vector store from documents"""
        if not documents:
            return
        
        # Split documents into chunks
        chunks = self.text_splitter.split_documents(documents)
        self.documents.extend(chunks)
        
        # Create embeddings
        texts = [doc.page_content for doc in chunks]
        embeddings_list = self.embeddings.embed_documents(texts)
        
        # Convert to numpy array
        embeddings_array = np.array(embeddings_list).astype('float32')
        
        # Create or update FAISS index
        if self.index is None:
            dimension = embeddings_array.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
        
        self.index.add(embeddings_array)
    
    def save_vector_store(self):
        """Save FAISS index and documents to disk"""
        os.makedirs("data", exist_ok=True)
        
        # Save FAISS index
        if self.index is not None:
            faiss.write_index(self.index, self.vector_store_path)
        
        # Save documents
        with open(self.docs_path, 'wb') as f:
            pickle.dump(self.documents, f)
    
    def load_vector_store(self) -> bool:
        """Load FAISS index and documents from disk"""
        try:
            if os.path.exists(self.vector_store_path) and os.path.exists(self.docs_path):
                self.index = faiss.read_index(self.vector_store_path)
                with open(self.docs_path, 'rb') as f:
                    self.documents = pickle.load(f)
                return True
        except Exception as e:
            print(f"Error loading vector store: {e}")
        return False
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Search for similar documents"""
        if self.index is None or len(self.documents) == 0:
            return []
        
        # Create query embedding
        query_embedding = self.embeddings.embed_query(query)
        query_vector = np.array([query_embedding]).astype('float32')
        
        # Search
        distances, indices = self.index.search(query_vector, min(k, len(self.documents)))
        
        # Return documents
        results = []
        for idx in indices[0]:
            if idx < len(self.documents):
                results.append(self.documents[idx])
        
        return results
    
    def generate_answer(self, query: str, context_docs: List[Document], client) -> str:
        """Generate answer using OpenAI with retrieved context"""
        # Prepare context
        context = "\n\n".join([
            f"Source: {doc.metadata.get('source', 'unknown')}\n{doc.page_content}"
            for doc in context_docs
        ])
        
        # Create prompt
        system_prompt = """You are a helpful assistant specialized in Singapore credit cards, rewards programs, and digital wallets. 
Use the provided context to answer questions accurately. If you don't know the answer based on the context, say so.
Be specific about miles per dollar (mpd), spending caps, and card-wallet combinations when relevant."""

        user_prompt = f"""Context:
{context}

Question: {query}

Please provide a detailed and accurate answer based on the context above. Include specific details like:
- Miles per dollar (mpd) rates
- Spending caps and minimum spends
- Card names and banks
- Compatible wallet-card combinations
- Any relevant terms and conditions"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
