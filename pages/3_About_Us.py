import streamlit as st

# region <--------- Streamlit App Configuration --------->
st.set_page_config(
    layout="centered",
    page_title="About Us - Credit Card Rewards Advisor",
    page_icon="ℹ️"
)
# endregion <--------- Streamlit App Configuration --------->

# Note: About page is accessible without login

st.title("ℹ️ About This App")

st.markdown("""
## Credit Card Rewards Advisor

### 🎯 Purpose
This application is designed to help Singaporeans optimize their credit card rewards and spending. 
Using advanced AI technology with Retrieval-Augmented Generation (RAG), the system provides 
intelligent recommendations based on a comprehensive knowledge base of Singapore credit cards.

### 🌟 Key Features

1. **💬 Intelligent Q&A System**
   - Ask natural language questions about credit cards
   - Get detailed answers about miles per dollar (mpd), spending caps, and card features
   - Understand complex card-wallet pairings and optimization strategies

2. **💳 Personal Spending Tracker**
   - Track spending across multiple credit cards
   - Visualize spending patterns by category and card
   - Export your spending data for analysis

3. **📄 Document Upload**
   - Upload additional PDF documents to expand the knowledge base
   - System automatically processes and indexes new information
   - Seamless integration with existing credit card knowledge

4. **🔐 User Authentication**
   - Secure login system with individual user accounts
   - Personal data isolation for each user
   - Track spending history per user

### 💾 Knowledge Base

Our system is built on a comprehensive database containing:
- **Credit Cards**: DBS, UOB, HSBC, Citi, Maybank, AMEX, Standard Chartered
- **Digital Wallets**: Kris+, Amaze, Atome
- **Loyalty Programs**: KrisFlyer, Asia Miles
- **Spending Categories**: Online, Dining, Travel, Groceries, Transport, and more
- **MCC Codes**: Detailed merchant category code mappings

### 👥 Who Is This For?

- **Miles Chasers**: Maximize airline miles and travel rewards
- **Cashback Optimizers**: Find the best cards for everyday spending
- **Card Collectors**: Manage and track multiple credit cards
- **Budget-Conscious Users**: Track spending and stay within limits

### 🛠️ Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **AI/ML**: OpenAI GPT-4, LangChain
- **Vector Database**: FAISS (Facebook AI Similarity Search)
- **Document Processing**: PyPDF for PDF parsing
- **Data Visualization**: Plotly, Pandas

### 📧 Contact & Support

For questions, feedback, or support:
- Email: support@creditcardadvisor.sg
- GitHub: github.com/creditcardadvisor

### 📜 Disclaimer

This application provides general information and recommendations based on publicly available data. 
Always verify credit card terms and conditions with the respective banks before making financial decisions. 
Rewards rates, caps, and terms are subject to change by card issuers.

---

*Last Updated: January 2025*
""")

st.markdown("---")

st.subheader("📊 App Statistics")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Credit Cards Tracked", "15+")

with col2:
    st.metric("Digital Wallets", "3+")

with col3:
    st.metric("Spending Categories", "11+")

st.markdown("---")

st.info("💡 **Tip**: Check out the Methodology page to learn how our RAG system works!")
