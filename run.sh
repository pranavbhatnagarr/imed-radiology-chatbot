#!/bin/bash

echo "🏥 Setting up I-MED Radiology Chatbot..."

# Check Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install it first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt -q

# Check .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create one with your GROQ_API_KEY."
    echo "   Example: echo 'GROQ_API_KEY=your_key_here' > .env"
    exit 1
fi

# Run scraper if data doesn't exist
if [ ! -f "data/procedures.json" ]; then
    echo "🔍 Scraping I-MED procedures..."
    python scraper/scrape.py
else
    echo "✅ Scraped data found, skipping scraper..."
fi

# Build vector store if it doesn't exist
if [ ! -d "data/chroma_db" ]; then
    echo "🧠 Building vector store..."
    python qa/embed.py
else
    echo "✅ Vector store found, skipping embedding..."
fi

# Launch the app
echo "🚀 Launching I-MED Radiology Assistant..."
streamlit run app.py