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
    """RAG System for credit card knowledge base (JSONL format) and uploaded documents"""

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

    # ============================================================================
    # MODIFIED METHOD: Load from JSONL instead of graph JSON
    # ============================================================================
    def load_credit_card_kb(self, jsonl_path: str = "data/faiss_kb_comprehensive.jsonl") -> List[Document]:
        """Load credit card knowledge base from JSONL file (one JSON object per line)"""
        documents = []
        try:
            with open(jsonl_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        line = line.strip()
                        if not line:  # Skip empty lines
                            continue
                        
                        data = json.loads(line)
                        
                        # Format the JSONL card data into readable text
                        text = self._format_card_chunk(data)
                        
                        # Create Document object with metadata
                        doc = Document(
                            page_content=text,
                            metadata={
                                "source": "credit_card_kb",
                                "card_name": data.get("card_name", "Unknown"),
                                "card_key": data.get("card_key", ""),
                                "domain": data.get("domain", ""),
                                "chunk_type": data.get("chunk_type", ""),
                                "keywords": ",".join(data.get("keywords", [])),
                                "doc_id": data.get("id", ""),
                                "issuer": data.get("metadata", {}).get("card_issuer", "")
                            }
                        )
                        documents.append(doc)
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON on line {line_num}: {e}")
                        continue
                    except Exception as e:
                        print(f"Error processing line {line_num}: {e}")
                        continue
        
        except FileNotFoundError:
            print(f"Error: File '{jsonl_path}' not found. Make sure faiss_kb_comprehensive.jsonl is in the current directory.")
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
        
        print(f"Loaded {len(documents)} documents from JSONL")
        return documents

    # ============================================================================
    # NEW METHOD: Load TNC PDFs from directory
    # ============================================================================
    def load_tnc_pdfs(self, tnc_dir: str = "data/TNC") -> List[Document]:
        """Load all PDF files from the TNC directory"""
        documents = []
        if not os.path.exists(tnc_dir):
            print(f"Warning: TNC directory '{tnc_dir}' not found.")
            return documents
            
        print(f"Loading TNC PDFs from {tnc_dir}...")
        
        for filename in os.listdir(tnc_dir):
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(tnc_dir, filename)
                try:
                    with open(file_path, 'rb') as f:
                        # Reuse existing process_pdf logic but adapt for local file path
                        # process_pdf expects a file-like object with a .name attribute
                        # We can just pass the file object since we opened it
                        pdf_docs = self.process_pdf(f)
                        
                        # Update metadata to indicate it's a TNC document
                        for doc in pdf_docs:
                            doc.metadata["source"] = filename
                            doc.metadata["type"] = "TNC"
                            doc.metadata["path"] = file_path
                            
                        documents.extend(pdf_docs)
                        print(f"Loaded TNC: {filename}")
                except Exception as e:
                    print(f"Error loading TNC PDF {filename}: {e}")
                    
        print(f"Loaded {len(documents)} chunks from {len(os.listdir(tnc_dir))} files in TNC directory")
        return documents

    # ============================================================================
    # NEW METHOD: Format card chunk data from JSONL
    # ============================================================================
    def _format_card_chunk(self, data: Dict) -> str:
        """Format card chunk data into readable text for embedding"""
        card_name = data.get("card_name", "Unknown Card")
        chunk_type = data.get("chunk_type", "")
        content = data.get("content", "")
        keywords = data.get("keywords", [])
        
        # Build formatted text
        text = f"Card: {card_name}\n"
        text += f"Category: {chunk_type}\n"
        text += f"Keywords: {', '.join(keywords)}\n"
        text += f"Details: {content}\n"
        
        return text

    # ============================================================================
    # KEEP EXISTING METHOD: Format entity (for backward compatibility if needed)
    # ============================================================================
    def _format_entity(self, data: Dict) -> str:
        """Format entity data into readable text (kept for backward compatibility)"""
        entity_type = data.get('type', 'Unknown')
        entity_id = data.get('id', '')
        props = data.get('properties', {})
        text = f"{entity_type}: {entity_id}\n"
        for key, value in props.items():
            text += f" {key}: {value}\n"
        return text

    # ============================================================================
    # KEEP EXISTING METHOD: Format relationship (for backward compatibility if needed)
    # ============================================================================
    def _format_relationship(self, data: Dict) -> str:
        """Format relationship data into readable text (kept for backward compatibility)"""
        source = data.get('source', '')
        target = data.get('target', '')
        relation = data.get('relation', '')
        props = data.get('properties', {})
        text = f"Relationship: {source} --[{relation}]--> {target}\n"
        for key, value in props.items():
            text += f" {key}: {value}\n"
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
            print("No documents to build vector store")
            return

        # Split documents into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # Create embeddings
        texts = [doc.page_content for doc in chunks]
        print(f"Creating embeddings for {len(texts)} chunks...")
        embeddings_list = self.embeddings.embed_documents(texts)

        # Convert to numpy array
        embeddings_array = np.array(embeddings_list).astype('float32')

        # Create or update FAISS index
        if self.index is None:
            dimension = embeddings_array.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings_array)
            print(f"FAISS index created with dimension {dimension}")
        else:
            self.index.add(embeddings_array)
            print(f"FAISS index updated")
            
        # Update documents list ONLY after successful embedding and indexing
        self.documents.extend(chunks)

    def save_vector_store(self):
        """Save FAISS index and documents to disk"""
        os.makedirs("data", exist_ok=True)

        # Save FAISS index
        if self.index is not None:
            faiss.write_index(self.index, self.vector_store_path)
            print(f"FAISS index saved to {self.vector_store_path}")

        # Save documents
        with open(self.docs_path, 'wb') as f:
            pickle.dump(self.documents, f)
        print(f"Documents saved to {self.docs_path}")

    def load_vector_store(self) -> bool:
        """Load FAISS index and documents from disk"""
        try:
            if os.path.exists(self.vector_store_path) and os.path.exists(self.docs_path):
                self.index = faiss.read_index(self.vector_store_path)
                with open(self.docs_path, 'rb') as f:
                    self.documents = pickle.load(f)
                print(f"Loaded {len(self.documents)} documents from disk")
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
            f"Card: {doc.metadata.get('card_name', 'Unknown')}\n"
            f"Type: {doc.metadata.get('chunk_type', '')}\n"
            f"Source: {doc.metadata.get('source', 'unknown')}\n"
            f"{doc.page_content}"
            for doc in context_docs
        ])

        # Create prompt
        system_prompt = """You are a helpful assistant specialized in Singapore credit cards, rewards programs, and digital wallets.

Use the provided context to answer questions accurately. If you don't know the answer based on the context, say so.

Be specific about miles per dollar (mpd), spending caps, minimum spends, and card-wallet combinations when relevant."""

        user_prompt = f"""Context:

{context}

Question: {query}

Please provide a detailed and accurate answer based on the context above. Include specific details like:

- Miles per dollar (mpd) rates
- Spending caps and minimum spends
- Card names and banks
- Compatible wallet-card combinations (Kris+, Amaze, Atome)
- Merchant Category Codes (MCCs) if relevant
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