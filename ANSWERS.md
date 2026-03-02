# ANSWERS.md — I-MED Radiology Chatbot

## Action Step 1: I-MED Email Reply

**Email sent to:** accounts@i-med.com.au
**Subject:** Patient query - MRI cost enquiry
**Date sent:** 28 February 2026

**Full reply received (automated response, received same day):**

> Thank you for reaching out to the I-MED Accounts Receivable team.
> If your enquiry is regarding a quote, booking, or requesting images or scans: Please note that our Accounts Receivable team are unable to assist with appointment bookings or quotes, or access to images or scan results. To ensure you receive the fastest service, we kindly ask you to Book online or find a clinic near you for quotes, enquiries or image requests.

**What this tells us about the chatbot:**
The reply confirms that I-MED does not provide pricing or cost information through any digital channel — not via email, and not on their public website. The accounts team explicitly states they cannot assist with quotes and redirects patients to call their local clinic directly. This means a patient asking the chatbot "how much does a knee MRI cost?" cannot be answered accurately. This is a fundamental data gap — category (a): the data does not exist publicly. No amount of improved scraping could fix this limitation.

---

## Action Step 2: Clinic Finder Scraper Output

**URL scraped:** https://i-med.com.au/find-a-radiology-clinic
**Total lines returned:** 895

**First 3 lines of raw output:**
```
Find a radiology clinic near you | I-MED Radiology Network
View site as:
Patient
```

**Observation:** The clinic finder page returned 895 lines but contained almost no structured clinic data — only navigation text, filters, and UI elements. The actual clinic listings are loaded dynamically via JavaScript after the page loads, which means our requests + BeautifulSoup scraper cannot access them. This confirms that clinic-specific information (addresses, phone numbers, opening hours) is inaccessible to my chatbot using the current scraping approach.

---

## Q1: Example Queries and System Responses

### Query 1: "What happens during an MRI scan?"

**System response:**
According to the MRI Scan procedure on the I-MED Radiology website, during an MRI scan, the procedure will be thoroughly explained to you, and your safety questionnaire reviewed and discussed before you enter the scan room. You will usually be asked to change into a gown, lie on the scan table, and given a buzzer to hold to communicate with the radiographer. The MRI scanner is very noisy, and you will be given earplugs or headphones to reduce the noise to safe levels. Depending on the type of MRI scan, you might have leads placed on your chest, a pulsoximeter on your finger, or a needle inserted into a vein in your arm for medication. The part of your body to be scanned will be carefully positioned and gently secured, and special antennae (coils) will be positioned around it to pick up signals from your body.

**Source:** https://i-med.com.au/procedures/mri-scan

---

### Query 2: "Do I need to fast before a CT scan?"

**System response:**
According to the CT Scan procedure on the I-MED Radiology website, some tests require fasting, while others do not. Specifically, Chest CT preparation requires a two hour fast, and Abdomen/pelvis CT requires a two hour fast. However, some tests require no preparation, including brain, sinus or facial bones, temporal bones, spine, knee or wrist, and CT scans of the bones. Whether you need to fast depends on the specific type of scan you are having. It is best to check with your doctor or the clinic for specific instructions.

**Source:** https://i-med.com.au/procedures/ct-scan

**Exact chunk retrieved to generate this answer:**
> "Many types of CT scan require an injection of an iodinated contrast material to show blood vessels and some organs. For these tests we will ask you to fast (not eat) prior to your appointment. Chest CT preparation: Two hour fast. Abdomen/pelvis CT & abdomen/pelvis + chest CT: Two hour fast. Some tests require no preparation, these include: brain, sinus or facial bones, temporal bones (inner ear), spine, knee or wrist, and CT scans of the bones."

**Similarity score:** 0.31 (ChromaDB cosine distance — lower = more relevant)

---

### Query 3: "Does Medicare cover X-ray?"

**System response:**
According to the General X-Ray procedure information, many x-rays are partially covered by a Medicare rebate, but the rebate from Medicare is often less than the actual cost of providing the service, resulting in a gap payment charged to the patient. However, pensioners and healthcare card holders are bulk billed for most Medicare rebateable imaging procedures.

**Source:** https://i-med.com.au/procedures/general-x-ray

---

## Q2: A Question My Chatbot Handled Poorly

### Query: "What are the risks of a PET scan?"

**Actual system response:**
The provided context does not mention the risks of a PET scan. The context only discusses MRI scans and CT scans, but does not provide information about PET scans. Therefore, I cannot provide an answer to this question based on the given context.

**Sources cited:**
- https://i-med.com.au/procedures/mri-scan
- https://i-med.com.au/procedures/ct-scan

**What went wrong:** This is a **retrieval problem**. PET scan was not one of the procedures I scraped, so there is no PET scan content in my vector store. However, the retrieval system still returned the closest matching chunks (MRI and CT scan pages) and passed them to the LLM. The LLM correctly refused to fabricate an answer, but it still cited irrelevant source URLs which is misleading — a patient might visit those pages expecting PET scan risk information and find none.

**Relevant code section:**
```python
def retrieve(query, n_results=5):
    embedding = model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results
    )
    chunks = []
    for i in range(len(results["documents"][0])):
        chunks.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "url": results["metadatas"][0][i]["url"],
            "score": results["distances"][0][i]
        })
    return chunks
```

**Root cause:** ChromaDB always returns the closest n results regardless of actual relevance. The fix would be to filter chunks by similarity threshold before passing to the LLM:
```python
filtered_chunks = [c for c in chunks if c["score"] < 0.8]
if not filtered_chunks:
    return "I could not find relevant information about that procedure."
```
This was a conscious decision — I preserved this behaviour as an honest example of a retrieval limitation rather than masking it.

---

## Q3: Things a Patient Would Ask That My Chatbot Cannot Answer

**1. "How much does a knee MRI cost at I-MED?"**
**Gap type: (a) Data does not exist on the website**
The website explicitly states fees vary and will be advised at time of booking. No specific pricing is published. Confirmed by Action Step 1 — the accounts team replied that they cannot provide quotes via email and redirected me to contact a local clinic directly. My chatbot handles this gracefully — when asked "How much does an MRI cost?" it responds:

> "The cost of an MRI is not explicitly stated in the provided context. To get an accurate answer, I would advise you to contact your local I-MED clinic directly by visiting i-med.com.au/find-a-radiology-clinic."

This behaviour was implemented after receiving the email reply in Action Step 1, by updating the system prompt to always redirect pricing questions to the clinic finder page.

**2. "What are the opening hours of the I-MED clinic in Parramatta?"**
**Gap type: (b) Data exists but my scraper could not access it**
The clinic finder page exists at i-med.com.au/find-a-radiology-clinic but all clinic listings are loaded dynamically via JavaScript. My requests + BeautifulSoup scraper retrieved 895 lines of navigation and UI text but zero actual clinic records. A Selenium or Playwright-based scraper would be needed to access this data.

**3. "What are the risks of a PET scan?"**
**Gap type: (a) Data does not exist in my scraped dataset**
PET scan was not included in the 7 procedures I scraped. The website does have a PET scan page, but I did not scrape it. This is a coverage gap in my dataset rather than a website limitation — it could be fixed by adding the PET scan URL to the scraper.

---

## Q4: CT Scan Chunking Analysis

The CT scan page at i-med.com.au/procedures/ct-scan produced **8 chunks** after scraping and embedding.

The three preparation types (brain CT, chest CT, abdomen/pelvis CT) ended up in the **same chunk** because my chunking strategy splits by word count (400 words, 50-word overlap) rather than by semantic section. Since all preparation instructions appear consecutively on the page, they were captured together in a single chunk.

**Query: "Do I need to fast before a chest CT scan?"**

**Actual system response:**
According to the CT Scan procedure on the I-MED Radiology website, for a Chest CT preparation, you are required to fast for 2 hours before the appointment, and you should take your medication as normal.

**Source:** https://i-med.com.au/procedures/ct-scan

**Assessment:** Because all three prep types landed in the same chunk, the chatbot performed well here — it had all the context it needed in one retrieval hit and correctly identified that chest CT requires a 2-hour fast. However, this is fortunate rather than by design. If the CT page were longer, the chest CT preparation section might have been split across chunk boundaries or merged with unrelated content, degrading retrieval quality. A more robust approach would use section-aware chunking that splits on HTML headings (h2, h3) rather than word count, ensuring each preparation type stays in its own chunk regardless of page length.

---

## Known Limitations

- **JavaScript-rendered content:** The scraper uses requests + BeautifulSoup and cannot execute JavaScript. Content hidden behind "Read more" buttons and dynamically loaded clinic data was not captured. Selenium or Playwright would be needed for complete coverage.
- **Pricing information:** I-MED does not publish specific procedure costs online. Confirmed via Action Step 1 — even direct email inquiry was redirected. Questions about cost cannot be answered.
- **Limited procedure coverage:** Only 7 procedures were scraped. PET scan, nuclear medicine, fluoroscopy, and other unscraped procedures will return no results.
- **Chunk boundary limitations:** Text is chunked by word count (400 words, 50-word overlap) rather than semantic sections. Related information can occasionally be split across chunks.
- **No session memory:** Each question is answered independently with no memory of previous questions in the conversation.
- **Clinic-specific information:** No clinic addresses, phone numbers, or opening hours were captured due to JavaScript rendering on the clinic finder page.