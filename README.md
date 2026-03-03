# I-MED Radiology Assistant 

A RAG-based Q&A chatbot that answers patient questions about radiology procedures at I-MED Radiology Network. All answers are grounded in content scraped from i-med.com.au — the system will not answer from general knowledge.

## How It Works

1. **Scraper** scrapes procedure pages from i-med.com.au and stores content as JSON
2. **Embedder** chunks the content and stores it in a local ChromaDB vector database using BAAI/bge-small-en-v1.5 embeddings
3. **Q&A engine** retrieves the most relevant chunks for a user query and passes them to Llama 3.3 70B via Groq API to generate a grounded answer with source citations

## Tech Stack

- `requests` + `BeautifulSoup` — web scraping
- `sentence-transformers` (BAAI/bge-small-en-v1.5) — semantic embeddings
- `ChromaDB` — local vector store
- `Groq` (Llama 3.3 70B) — LLM for answer generation
- `Streamlit` — web UI

## Setup Instructions

### Prerequisites
- Python 3.9+
- A free Groq API key from [console.groq.com](https://console.groq.com)

### One-Command Setup
```bash
# 1. Clone the repo
git clone https://github.com/pranavbhatnagarr/imed-radiology-chatbot.git
cd imed-radiology-chatbot

# 2. Add your Groq API key
echo "GROQ_API_KEY=your_key_here" > .env

# 3. Run everything
bash run.sh
```

The app will open at http://localhost:8501

### Docker Setup (Alternative)
```bash
# 1. Clone the repo
git clone https://github.com/pranavbhatnagarr/imed-radiology-chatbot.git
cd imed-radiology-chatbot

# 2. Add your Groq API key
echo "GROQ_API_KEY=your_key_here" > .env

# 3. Build and run with Docker
docker-compose up --build
```

The app will open at http://localhost:8501

> No Python installation required — Docker handles everything automatically.

## Example Queries and Outputs

**Query 1: "What happens during an MRI scan?"**
> According to the MRI Scan procedure on the I-MED Radiology website, during an MRI scan, the procedure will be thoroughly explained to you, and your safety questionnaire reviewed before you enter the scan room. You will be asked to change into a gown, lie on the scan table, and given a buzzer to communicate with the radiographer.
> Source: https://i-med.com.au/procedures/mri-scan

**Query 2: "Do I need to fast before a CT scan?"**
> Some CT scans require fasting and others do not. Chest CT and abdomen/pelvis CT require a two hour fast. Brain, sinus, spine, knee and wrist CT scans require no preparation.
> Source: https://i-med.com.au/procedures/ct-scan

**Query 3: "Does Medicare cover X-ray?"**
> Many x-rays are partially covered by a Medicare rebate, but the rebate is often less than the actual cost, resulting in a gap payment. Pensioners and healthcare card holders are bulk billed for most Medicare rebateable imaging procedures.
> Source: https://i-med.com.au/procedures/general-x-ray

**Query 4: "How do I prepare for an ultrasound?"**
> You should read any instructions given by your doctor, wear clothing that provides easy access to the area being imaged, and bring any previous ultrasound films. An abdomen ultrasound requires fasting for six hours prior to the examination.
> Source: https://i-med.com.au/procedures/ultrasound

**Query 5: "What are the risks of an X-ray?"**
> At the radiation dose levels used in diagnostic radiography there is little or no evidence of health effects. The two major risks are cancer occurring many years after radiation exposure, and health problems in children born to people exposed to radiation. To put this in perspective, a patient would need approximately 38 chest x-rays to receive radiation similar to one year of normal background radiation.
> Source: https://i-med.com.au/procedures/general-x-ray


## Known Limitations

- **Pricing information:** I-MED does not publish specific procedure costs online. Confirmed via Action Step 1 — even direct email inquiry was redirected. Questions about cost cannot be answered.
- **Limited procedure coverage:** Only 7 procedures were scraped. PET scan, nuclear medicine, fluoroscopy, and other unscraped procedures will return no results.
- **Chunk boundary limitations:** Text is chunked by word count (400 words, 50-word overlap) rather than semantic sections. Related information can occasionally be split across chunks.
- **No session memory:** Each question is answered independently with no memory of previous questions in the conversation.
- **Clinic-specific information:** The scraper captures clinic names, addresses, and phone numbers from the clinic listing page. However, opening hours and other clinic-specific details are likely contained on individual clinic detail pages (“View clinic information”), which were not scraped in this submission.