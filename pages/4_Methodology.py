import streamlit as st

# Page config
st.set_page_config(
    page_title="Methodology",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Methodology")

st.markdown("""
## How Our RAG System Works

This page explains the technical methodology behind our Credit Card Rewards Advisor system.

---

### 🧠 What is RAG (Retrieval-Augmented Generation)?

RAG is an AI framework that combines:
1. **Retrieval**: Finding relevant information from a knowledge base
2. **Augmentation**: Adding that information to the AI's context
3. **Generation**: Using AI to generate accurate, context-aware responses

This approach ensures our answers are:
- **Accurate**: Based on actual data, not hallucinations
- **Up-to-date**: Uses your knowledge base and uploaded documents
- **Traceable**: You can see which sources were used
""")

st.markdown("---")

# Architecture diagram using columns
st.subheader("🏗️ System Architecture")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 1️⃣ Data Ingestion
    - Load credit card knowledge base (JSON Lines)
    - Parse entity relationships (cards, wallets, banks)
    - Process uploaded PDF documents
    - Convert to structured text chunks
    """)

with col2:
    st.markdown("""
    ### 2️⃣ Vectorization
    - Split text into chunks (1000 chars)
    - Generate embeddings using OpenAI
    - Store in FAISS vector database
    - Enable semantic similarity search
    """)

with col3:
    st.markdown("""
    ### 3️⃣ Query & Generation
    - User asks a question
    - Convert query to embedding
    - Find top-k similar documents
    - Generate answer with GPT-4
    """)

st.markdown("---")

st.subheader("🔄 RAG Workflow")

st.markdown("""
```
User Question
    ↓
[1] Query Embedding
    ↓
[2] Similarity Search (FAISS)
    ↓
[3] Retrieve Top-K Documents
    ↓
[4] Context Preparation
    ↓
[5] LLM Prompt Construction
    ↓
[6] GPT-4 Generation
    ↓
Response to User
```
""")

st.markdown("---")

st.subheader("🔧 Technical Components")

# Create tabs for different technical aspects
tab1, tab2, tab3, tab4 = st.tabs(["Document Processing", "Embeddings", "Vector Store", "LLM Integration"])

with tab1:
    st.markdown("""
    ### Document Processing Pipeline
    
    #### Credit Card Knowledge Base
    - **Format**: JSON Lines (one JSON object per line)
    - **Entities**: Cards, Banks, Wallets, Categories, MCC Codes
    - **Relationships**: earns_on, pairs_with, transfer_to, excluded_by
    - **Processing**: Parse JSON → Format to readable text → Create Document objects
    
    #### PDF Upload
    - **Library**: PyPDF
    - **Process**: Extract text per page → Create Document objects with metadata
    - **Metadata**: Source filename, page number
    
    #### Text Splitting
    - **Method**: RecursiveCharacterTextSplitter (LangChain)
    - **Chunk Size**: 1000 characters
    - **Overlap**: 200 characters (ensures context continuity)
    """)
    
    st.code("""
# Example: Processing credit card entity
Entity: Card:dbs_wwbc
  name: DBS Woman's World Card
  bank: DBS
  base_mpd: 0.4
  annual_fee: ~S$196
  notes: online bonus 4 mpd; overseas 1.2 mpd
    """, language="text")

with tab2:
    st.markdown("""
    ### Embeddings Generation
    
    **What are Embeddings?**
    - Vector representations of text in high-dimensional space
    - Semantically similar texts have similar vectors
    - Enable mathematical similarity comparisons
    
    **Our Implementation:**
    - **Model**: OpenAI `text-embedding-3-small`
    - **Dimension**: 1536 dimensions
    - **Process**: Text → API Call → Vector array
    
    **Example:**
    ```python
    Query: "best card for dining"
    Embedding: [0.023, -0.015, 0.041, ..., 0.008]  # 1536 numbers
    
    Document: "Card earns 4 mpd on dining"
    Embedding: [0.021, -0.014, 0.039, ..., 0.009]  # Similar!
    
    Distance: Very close → High relevance
    ```
    """)
    
    st.info("💡 **Why embeddings?** They capture semantic meaning, so 'dining' and 'restaurants' are treated as similar, even though they're different words.")

with tab3:
    st.markdown("""
    ### FAISS Vector Store
    
    **Facebook AI Similarity Search (FAISS)**
    - High-performance library for similarity search
    - Optimized for large-scale vector databases
    - Fast nearest neighbor search
    
    **Our Configuration:**
    - **Index Type**: IndexFlatL2 (exact L2 distance)
    - **Distance Metric**: Euclidean distance (L2)
    - **Storage**: Persistent storage to disk
    
    **Search Process:**
    1. Convert query to embedding vector
    2. FAISS finds k-nearest neighbors
    3. Return most similar document chunks
    4. Typical k=5 (top 5 results)
    
    **Performance:**
    - Search time: <100ms for 1000s of documents
    - Memory efficient
    - Scalable to millions of vectors
    """)
    
    st.code("""
# FAISS search example
query_vector = embeddings.embed_query("best dining card")
distances, indices = index.search(query_vector, k=5)

# Results ranked by similarity
# Lower distance = Higher similarity
    """, language="python")

with tab4:
    st.markdown("""
    ### LLM Integration (GPT-4)
    
    **Model**: GPT-4o-mini
    - Fast and cost-effective
    - Strong reasoning capabilities
    - Good at following instructions
    
    **Prompt Engineering:**
    
    **System Prompt:**
    - Define role as credit card expert
    - Set behavior guidelines
    - Specify answer format requirements
    
    **User Prompt:**
    - Include retrieved context (5 documents)
    - Add user question
    - Request specific details (mpd, caps, etc.)
    
    **Temperature**: 0.3 (low for factual accuracy)
    **Max Tokens**: 1000 (detailed responses)
    
    **Context Window:**
    ```
    System: You are a credit card expert...
    
    Context:
    [Document 1: DBS Woman's World Card info]
    [Document 2: Online shopping category info]
    [Document 3: Wallet pairing details]
    ...
    
    Question: Which card is best for online shopping?
    
    Answer: [GPT-4 generates response using context]
    ```
    """)

st.markdown("---")

st.subheader("📊 Data Structure")

st.markdown("""
### Knowledge Graph Structure

Our credit card knowledge base is structured as a **knowledge graph**:

**Entities (Nodes):**
- 💳 **Cards**: 15+ Singapore credit cards
- 🏦 **Banks**: DBS, UOB, HSBC, Citi, etc.
- 📱 **Wallets**: Kris+, Amaze, Atome
- 🏷️ **Categories**: Dining, Travel, Online, etc.
- 🔢 **MCC Codes**: Merchant category codes

**Relationships (Edges):**
- `earns_on`: Card → Category (e.g., "4 mpd on dining")
- `pairs_with`: Card → Wallet (e.g., "works with Kris+")
- `transfer_to`: Card → Loyalty Program
- `excluded_by`: Wallet → Bank (e.g., "Amaze doesn't work with UOB")
- `belongs_to`: MCC → Category

This graph structure enables:
- Complex multi-hop reasoning
- Relationship-based queries
- Comprehensive recommendations
""")

st.markdown("---")

st.subheader("🎯 Key Advantages of Our Approach")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### ✅ Benefits
    - **Accuracy**: Grounded in real data
    - **Transparency**: View source documents
    - **Extensibility**: Add new documents easily
    - **Personalization**: User-specific tracking
    - **Offline Capability**: Local vector store
    - **Cost Efficient**: Only query LLM when needed
    """)

with col2:
    st.markdown("""
    ### 🚀 Improvements Over Pure LLM
    - Reduces hallucinations
    - Provides citation sources
    - Uses latest information
    - Handles specialized domain knowledge
    - Maintains consistency
    - Better for factual queries
    """)

st.markdown("---")

st.subheader("🔮 Future Enhancements")

st.markdown("""
Potential improvements to the system:

1. **🔄 Auto-Update**: Periodic refresh of credit card data from bank websites
2. **📊 Analytics**: ML-powered spending predictions and recommendations
3. **🎨 UI/UX**: Enhanced visualizations and interactive card comparisons
4. **🔔 Alerts**: Notify users of new card promotions matching their spending patterns
5. **🤝 Multi-Modal**: Support for images (card benefits, terms & conditions)
6. **🌐 API**: RESTful API for third-party integrations
7. **📱 Mobile App**: Native mobile experience
8. **🔐 Advanced Security**: Encryption for sensitive financial data
""")

st.markdown("---")

st.info("""
📚 **Learn More:**
- [LangChain Documentation](https://python.langchain.com/)
- [FAISS Library](https://github.com/facebookresearch/faiss)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [RAG Overview](https://www.pinecone.io/learn/retrieval-augmented-generation/)
""")
