# Credit Card Rewards Advisor - RAG System
import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from openai import OpenAI
from helper_functions.auth import login_page, require_login, display_user_header
from helper_functions.rag_helper import RAGSystem

# Load environment variables
if load_dotenv('.env'):
    OPENAI_KEY = os.getenv('OPENAI_API_KEY')
else:
    OPENAI_KEY = st.secrets['OPENAI_API_KEY']

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_KEY)

# region <--------- Streamlit App Configuration --------->
st.set_page_config(
    layout="wide",
    page_title="Credit Card Rewards Advisor",
    page_icon="💳",
    initial_sidebar_state="expanded"
)
# endregion <--------- Streamlit App Configuration --------->

# Check login
if not require_login():
    login_page()
else:
    # Display user info in sidebar
    display_user_header()
    
    # Initialize RAG system
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = RAGSystem(OPENAI_KEY)
        
        # Try to load existing vector store
        if not st.session_state.rag_system.load_vector_store():
            # If no existing store, build from credit card KB
            with st.spinner("🔄 Initializing knowledge base..."):
                kb_docs = st.session_state.rag_system.load_credit_card_kb()
                st.session_state.rag_system.build_vector_store(kb_docs)
                st.session_state.rag_system.save_vector_store()
    
    # Main content
    st.title("💳 Credit Card Rewards Advisor")
    st.markdown("### AI-Powered Credit Card Recommendations for Singapore")
    
    st.markdown("""
    Ask questions about credit cards, rewards programs, and optimize your spending!
    Examples:
    - *"Which card is best for online shopping?"*
    - *"Can I use Amaze wallet with DBS Woman's World Card?"*
    - *"What's the best card for dining rewards?"*
    - *"How many miles per dollar can I get with Citi Rewards on Grab?"*
    """)
    
    # Create tabs
    tab1, tab2 = st.tabs(["🤖 Ask Questions", "📄 Upload Documents"])
    
    with tab1:
        st.subheader("Ask About Credit Cards")
        
        # Chat interface
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # User input
        user_question = st.chat_input("Ask a question about credit cards...")
        
        if user_question:
            # Add user message to chat
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            
            with st.chat_message("user"):
                st.markdown(user_question)
            
            # Generate response
            with st.chat_message("assistant"):
                with st.spinner("🔍 Searching knowledge base..."):
                    # Retrieve relevant documents
                    relevant_docs = st.session_state.rag_system.similarity_search(user_question, k=5)
                    
                    # Generate answer
                    answer = st.session_state.rag_system.generate_answer(
                        user_question,
                        relevant_docs,
                        client
                    )
                    
                    st.markdown(answer)
                    
                    # Show sources
                    with st.expander("📚 View Sources"):
                        for i, doc in enumerate(relevant_docs, 1):
                            st.markdown(f"**Source {i}:**")
                            st.text(doc.page_content[:300] + "...")
                            st.markdown("---")
            
            # Add assistant response to chat
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
        
        # Clear chat button
        if st.session_state.chat_history:
            if st.button("🗑️ Clear Chat History"):
                st.session_state.chat_history = []
                st.rerun()
    
    with tab2:
        st.subheader("Upload Additional Documents")
        st.markdown("""
        Upload PDF documents to expand the knowledge base with additional information.
        The system will process and index your documents for answering questions.
        """)
        
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type=["pdf"],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            if st.button("📥 Process Documents", type="primary"):
                with st.spinner("Processing documents..."):
                    all_docs = []
                    for uploaded_file in uploaded_files:
                        docs = st.session_state.rag_system.process_pdf(uploaded_file)
                        all_docs.extend(docs)
                        st.success(f"✅ Processed: {uploaded_file.name}")
                    
                    # Add to vector store
                    if all_docs:
                        st.session_state.rag_system.build_vector_store(all_docs)
                        st.session_state.rag_system.save_vector_store()
                        st.success(f"🎉 Successfully indexed {len(all_docs)} document chunks!")
        
        # Show statistics
        st.markdown("---")
        st.subheader("📊 Knowledge Base Statistics")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Documents", len(st.session_state.rag_system.documents))
        with col2:
            if st.session_state.rag_system.index:
                st.metric("Vector Store Size", st.session_state.rag_system.index.ntotal)
