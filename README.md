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

**Query 1: "What is iodinated contrast used for in a CT scan?"**
> According to the CT Scan procedure on the I-MED Radiology website, iodinated contrast is used to outline specific parts of the body, such as the intestine, and to help the radiologist make an accurate diagnosis. It can be administered through an injection into a vein in the arm or hand, or as a drink to outline the intestine. The iodinated contrast helps to provide clearer images of the area being scanned.
> Source: https://i-med.com.au/procedures/ct-scan

**Query 2: "What happens if I am claustrophobic during an MRI?"**
> According to the MRI Scan procedure, if you are claustrophobic and find you are unable to proceed with the scan, a sedative can be administered. You are advised to discuss this with your doctor and inform the radiology practice before having the scan. Additionally, you can ask your GP to prescribe a sedative that you can take before arriving, and ensure you have a designated driver to take you to and from the clinic.
> Source: https://i-med.com.au/procedures/mri-scan

**Query 3: "I have diabetes. Do I need to tell the clinic before my CT scan?"**
> According to the CT Scan procedure information, if you have diabetes, you should inform the clinic before your appointment. The context states that "All patients are asked if they have kidney disease, diabetes or if taking metformin. If ‘yes’ to any of the above, ask patient to bring copies of recent blood tests (within the last 3 months) to their appointment." Additionally, it is mentioned that "It is important that the need to fast does not affect you if you have special dietary requirements (e.g. diabetes). Please check with your doctor or our clinic if you have any concerns." It is also noted that "Safety information for diabetics" is provided, which includes information about the potential malfunction of diabetic equipment, such as CGM and insulin pumps, when exposed to x-rays. Patients with diabetes are advised to notify staff of any diabetic equipment attached to them prior to the procedure.
> Source: https://i-med.com.au/procedures/ct-scan

**Query 4: "How does an ultrasound work and how much would it cost me?"**
> According to the Ultrasound procedure information, an ultrasound examination uses high-frequency sound waves to produce an image onto a screen that shows the inside of your body. The examination is performed using a smooth, hand-held device called a transducer that is moved across the body with a sliding and rotating action.
> Regarding the cost, the information provided in the Ultrasound procedure section states that fees for radiology procedures vary and depend on several factors. To get an accurate estimate of the cost, I would advise you to contact your local I-MED clinic directly by visiting i-med.com.au/find-a-radiology-clinic. They will be able to provide you with more information on the fees associated with your examination.
> Source: https://i-med.com.au/procedures/ultrasound

**Query 5: "Why is the sky blue?"**
> I could not find relevant information about that in the I-MED procedure database. Please try rephrasing your question or ask about a specific procedure like General X-Ray, Lung Screening, Cardiac Services, Mammography, MRI, CT scan, or Ultrasound.


## Known Limitations

- **Pricing information:** I-MED does not publish specific procedure costs online. Confirmed via Action Step 1 — even direct email inquiry was redirected. Questions about cost cannot be answered.
- **Limited procedure coverage:** Only 7 procedures were scraped. PET scan, nuclear medicine, Angiography, and other unscraped procedures will return no results.
- **Chunk boundary limitations:** Text is chunked by word count (400 words, 50-word overlap) rather than semantic sections. Related information can occasionally be split across chunks.
- **No session memory:** Each question is answered independently with no memory of previous questions in the conversation.
- **Clinic-specific information:** The scraper captures clinic names, addresses, and phone numbers from the clinic listing page. However, opening hours and other clinic-specific details are likely contained on individual clinic detail pages (“View clinic information”), which were not scraped in this submission.