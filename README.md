# 💳 Credit Card Rewards Advisor - RAG System

An intelligent AI-powered application to help Singapore users optimize credit card rewards using Retrieval-Augmented Generation (RAG).

## 🌟 Features

### Core Features (Assignment Requirements)
- ✅ **Simple Login System**: Hardcoded authentication with user registration
- ✅ **Document Upload**: Upload PDF files to expand the knowledge base
- ✅ **RAG-enabled Q&A**: Ask questions about credit cards and get AI-powered answers
- ✅ **About Us Page**: Comprehensive information about the application
- ✅ **Methodology Page**: Detailed explanation of how the RAG system works

### Additional Features
- 💳 **Personal Spending Tracker**: Track spending across multiple credit cards
- 📊 **Analytics Dashboard**: Visualize spending patterns by category and card
- 👤 **User Profiles**: Individual user accounts with isolated data
- 🔍 **Semantic Search**: FAISS-powered vector similarity search
- 📚 **Source Citations**: View which documents were used to generate answers
- 💾 **Persistent Storage**: Save and load vector store for faster startup

## 🏗️ Technology Stack

- **Frontend**: Streamlit
- **AI/ML**: OpenAI GPT-4o-mini, LangChain
- **Vector Database**: FAISS (Facebook AI Similarity Search)
- **Document Processing**: PyPDF
- **Data Visualization**: Plotly, Pandas
- **Authentication**: Custom JSON-based user management

## 📋 Prerequisites

- Python 3.8+
- OpenAI API Key

## 🚀 Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd ai-champ-project
```

2. **Install dependencies**
```bash
pip install -r requirements_new.txt
```

3. **Set up environment variables**

Create a `.env` file in the root directory:
```
OPENAI_API_KEY=your_openai_api_key_here
```

Or use Streamlit secrets (for deployment):
Create `.streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = "your_openai_api_key_here"
```

4. **Run the application**
```bash
streamlit run main.py
```

The app will open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
ai-champ-project/
│
├── main.py                          # Main application entry point
├── requirements_new.txt             # Python dependencies
├── README.md                        # This file
├── .env                            # Environment variables (create this)
│
├── data/                           # Data storage
│   ├── credit-card-kb.json        # Credit card knowledge base
│   ├── users.json                 # User credentials (auto-generated)
│   ├── user_spending.json         # User spending data (auto-generated)
│   ├── faiss_index                # FAISS vector store (auto-generated)
│   └── documents.pkl              # Processed documents (auto-generated)
│
├── helper_functions/              # Helper modules
│   ├── auth.py                   # Authentication and user management
│   ├── rag_helper.py             # RAG system implementation
│   ├── spending_tracker.py       # Spending tracking functionality
│   └── llm.py                    # LLM utility functions
│
├── logics/                       # Business logic
│   └── customer_query_handler.py # Query processing logic
│
└── pages/                        # Streamlit pages
    ├── 1_💳_Spending_Tracker.py  # Spending tracker page
    ├── 3_About_Us.py              # About page
    └── 4_📊_Methodology.py        # Methodology explanation
```

## 🎯 Usage Guide

### 1. Login / Registration

**Default Admin Account:**
- Username: `admin`
- Password: `password123`

Or register a new account:
- Click "Register" tab
- Enter username, email, and password
- Login with your new credentials

### 2. Ask Questions

Navigate to the main page and ask questions like:
- "Which card is best for online shopping?"
- "Can I use Amaze wallet with DBS Woman's World Card?"
- "What's the best card for dining rewards?"
- "How many miles per dollar can I get with Citi Rewards?"

The system will:
1. Search the knowledge base
2. Retrieve relevant information
3. Generate a comprehensive answer
4. Show source documents used

### 3. Upload Documents

Go to the "Upload Documents" tab:
1. Click "Choose PDF files"
2. Select one or more PDF files
3. Click "Process Documents"
4. Files will be indexed and added to the knowledge base

### 4. Track Spending

Navigate to "Spending Tracker" page:
- **Dashboard**: View analytics and charts
- **Add Spending**: Record new transactions
- **Manage Entries**: Edit or delete transactions

## 📊 Knowledge Base

The system includes information about:

- **15+ Credit Cards** from major Singapore banks
- **3+ Digital Wallets** (Kris+, Amaze, Atome)
- **11+ Spending Categories**
- **MCC Codes** and their mappings
- **Loyalty Programs** (KrisFlyer, Asia Miles)
- **Card-Wallet Pairings** and optimization strategies

## 🔧 Configuration

### Customize RAG Parameters

In `helper_functions/rag_helper.py`:

```python
# Adjust chunk size for document splitting
chunk_size = 1000      # Characters per chunk
chunk_overlap = 200    # Overlap between chunks

# Modify search parameters
k = 5                  # Number of documents to retrieve

# Adjust LLM parameters
temperature = 0.3      # Lower = more factual
max_tokens = 1000     # Maximum response length
```

### Add New Credit Cards

Edit `data/credit-card-kb.json` following the JSON Lines format:

```json
{"id":"card:new_card","type":"Card","properties":{"name":"New Card","bank":"Bank","base_mpd":"1.2"}}
{"source":"card:new_card","target":"cat:dining","relation":"earns_on","properties":{"mpd":"4"}}
```

## 🐛 Troubleshooting

### FAISS Import Error
If you encounter issues with FAISS on Apple Silicon:
```bash
pip install faiss-cpu --no-cache-dir
```

### OpenAI API Key Error
Ensure your `.env` file exists and contains:
```
OPENAI_API_KEY=sk-...
```

### Vector Store Not Loading
Delete the existing index and rebuild:
```bash
rm data/faiss_index data/documents.pkl
# Restart the app
```

## 📚 Assignment Compliance

This project fulfills the **Group of 1 (Individual)** requirements:

✅ **Single RAG Feature**: Q&A based on credit card knowledge base and uploaded PDFs  
✅ **Simple UI**: Streamlit interface with multiple pages  
✅ **Hardcoded Protection**: Authentication system with user management  
✅ **LLM Integration**: OpenAI GPT-4o-mini  
✅ **Local File-based Store**: FAISS vector database  
✅ **Static Uploaded Documents**: PDF processing and indexing  
✅ **About Us Page**: Comprehensive app information  
✅ **Methodology Page**: Detailed RAG system explanation  

**Bonus Features:**
- User registration and individual profiles
- Personal spending tracker with analytics
- Persistent vector store
- Source citation for answers

## 🤝 Contributing

This is an educational project for an AI assignment. Suggestions and improvements are welcome!

## 📄 License

This project is for educational purposes only.

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- LangChain for RAG framework
- FAISS for vector similarity search
- Streamlit for the web interface

---

**Created for**: AI Champions Bootcamp Assignment  
**Date**: January 2025  
**Author**: [Your Name]
