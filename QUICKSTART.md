# 🚀 Quick Start Guide

## Step 1: Install Dependencies

```bash
pip install -r requirements_new.txt
```

## Step 2: Set Up OpenAI API Key

Create a `.env` file in the project root:

```bash
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

Replace `your_openai_api_key_here` with your actual OpenAI API key.

## Step 3: Run the Application

```bash
streamlit run main.py
```

The app will open automatically in your browser at `http://localhost:8501`

## Step 4: Login

**Option 1: Use Default Admin Account**
- Username: `admin`
- Password: `password123`

**Option 2: Register New Account**
- Click "Register" tab
- Fill in username, email, and password
- Click "Register"
- Go back to "Login" tab and login

## Step 5: Try the Features

### 💬 Ask Questions
On the main page, try asking:
- "Which card gives the best rewards for online shopping?"
- "Can I use Kris+ with DBS Woman's World Card?"
- "What's the miles per dollar for Citi Rewards on dining?"

### 📄 Upload Documents
- Click "Upload Documents" tab
- Upload any PDF file with credit card information
- Click "Process Documents"
- System will index the content

### 💳 Track Spending
- Go to "Spending Tracker" page (sidebar)
- Add your credit card transactions
- View analytics and charts

### ℹ️ Learn More
- Check "About Us" page for app information
- Read "Methodology" page to understand how RAG works

## 🎯 Example Questions to Ask

1. **Card Recommendations**
   - "What's the best card for dining in Singapore?"
   - "Which card should I use for overseas spending?"

2. **Wallet Pairings**
   - "Does Amaze work with UOB cards?"
   - "How do I maximize rewards with Kris+?"

3. **Technical Details**
   - "What MCC code does Grab use?"
   - "What are the spending caps for HSBC Revolution?"

4. **Comparisons**
   - "Compare DBS Woman's World vs Citi Rewards for online shopping"
   - "Which gives more miles: Maybank XL or UOB PPV?"

## 🐛 Common Issues

### Issue: ModuleNotFoundError
**Solution**: Install all dependencies
```bash
pip install -r requirements_new.txt
```

### Issue: OpenAI API Error
**Solution**: Check your `.env` file has the correct API key

### Issue: FAISS Error on Mac
**Solution**: 
```bash
pip install --no-cache-dir faiss-cpu
```

## 📊 Sample Spending Entry

Try adding this to your spending tracker:
- **Card**: DBS Woman's World Card
- **Category**: Online Shopping
- **Amount**: 150.00
- **Date**: Today
- **Notes**: Lazada purchase

## 🎉 You're All Set!

Enjoy exploring Singapore credit card rewards with AI! 🚀
