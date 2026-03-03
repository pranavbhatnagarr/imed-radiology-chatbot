# ANSWERS.md — I-MED Radiology Chatbot

## Action Step 1: I-MED Email Reply

**Email sent to:** accounts@i-med.com.au
**Subject:** Patient query - MRI cost enquiry
**Date sent:** 28 February 2026

**Full reply received (automated response, received same day):**

> Thank you for reaching out to the I-MED Accounts Receivable team.
> If your enquiry is regarding a quote, booking, or requesting images or scans: Please note that our Accounts Receivable team are unable to assist with appointment bookings or quotes, or access to images or scan results. To ensure you receive the fastest service, we kindly ask you to Book online or find a clinic near you for quotes, enquiries or image requests.

**What this tells us about the chatbot:**
The reply confirms that I-MED does not provide pricing or cost information through any digital channel, not via email, and not on their public website. The accounts team explicitly states they cannot assist with quotes and redirects patients to call their local clinic directly. This means a patient asking the chatbot "how much does a knee MRI cost?" cannot be answered accurately. No amount of improved scraping could fix this limitation.

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

**Observation:** The clinic finder page returned 895 lines and did include structured clinic listing data (clinic names, addresses, and phone numbers). This confirms the listing content is accessible using requests + BeautifulSoup. However, the listing page does not include opening hours; those appear to require opening each clinic’s “View clinic information” page. Since my scraper only collected top-level listings, my chatbot cannot answer opening-hours questions without extending the scraper to follow each clinic detail link.

---

## Q1: Example Queries and System Responses

### Query 1: "What happens during an MRI scan?"

**System response:**
According to the MRI Scan procedure, during an MRI scan, the procedure will be thoroughly explained to you, and your safety questionnaire reviewed and discussed before you enter the scan room. You will usually be asked to change into a gown and lie on the scan table, and given a buzzer to hold to communicate with the radiographer. The MRI scanner is very noisy, so you will be given earplugs or headphones to reduce the noise to safe levels. Depending on the type of MRI scan, you might have leads placed on your chest, a pulsoximeter on your finger, or a needle inserted into a vein in your arm for medication. The part of your body to be scanned will be carefully positioned and secured, and special antennae (coils) will be placed around it to pick up signals for the computer to create images.

**Source:** https://i-med.com.au/procedures/mri-scan

**Exact chunk retrieved to generate this answer:**
> "might like to review the older studies or see if your condition has changed since your last scan. What happens during an MRI scan? keyboard_arrow_down The MRI scan procedure will be thoroughly explained to you, and your safety questionnaire reviewed and discussed before you enter the scan room. If you have any questions, please ask the radiographer (medical imaging technologist), who will be operating the MRI scanner, as it is important that you are comfortable and know what will be happening. You will usually be asked to change into a gown to avoid items in your pockets being accidentally taken into the scan room. You will be asked to lie on the scan table and given a buzzer to hold. When you squeeze it, an alarm sounds in the control room and you will be able to talk to the radiographer. The MRI scanner is very noisy during the scans. It is at a noise level that can damage your hearing. You will be given earplugs or headphones to reduce the noise to safe levels. Depending on the type of MRI scan you are having and your particular situation, you might have: leads placed on your chest to monitor your heartbeat if having a heart scan a small plastic tube (pulsoximeter) taped on your finger to check your breathing and heart rate if having sedative (calming) medication a needle inserted into a vein in your arm if any medication is required during the scan If you are claustrophobic and find you are unable to proceed with the scan, a sedative can be administered. Please talk to you referring practitioner if you have any queries or concerns regarding this. The most common medication injected is called Gadolinium contrast medium (contrast). This highlights the part of the body being scanned, which can give more information to the radiologist who is assessing your problem. Other medication might be injected; for example, to slow down your intestinal movement if having an MRI of the rectum. The part of your body to be scanned will be carefully positioned and gently secured, so you are comfortable and more likely to remain still. Special antennae (coils) will be positioned around it to pick up signals from your body so the computer can create images. The coils are usually encased in a plastic pad or frame. Depending on the part of the body being scanned, they might be"

**Similarity score:** 0.2882266938686371 (ChromaDB cosine distance: lower = more relevant)

---

### Query 2: "Do I need to fast before a CT scan?"

**System response:**
According to the CT Scan procedure on the I-MED Radiology website, some tests require fasting prior to the appointment. Specifically, it is mentioned that chest CT preparation requires a two-hour fast, and abdomen/pelvis CT & abdomen/pelvis + chest CT also require a two-hour fast. However, it is also stated that some tests, such as brain, sinus or facial bones, temporal bones (inner ear), spine, knee or wrist, and CT scans of the bones, require no preparation. It is recommended to check with your doctor or the clinic if you have any concerns, especially if you have special dietary requirements, such as diabetes.

**Source:** https://i-med.com.au/procedures/ct-scan

---

### Query 3: "Does Medicare cover X-ray?"

**System response:**
According to the General X-Ray procedure information, many x-rays are partially covered by a Medicare rebate, meaning the rebate from Medicare is often less than the actual cost of providing the service. However, the extent of Medicare coverage may vary depending on the type and number of tests, and the complexity. Pensioners and healthcare card holders are bulk billed for most Medicare rebateable imaging procedures.

**Source:** https://i-med.com.au/procedures/general-x-ray

---

## Q2: A Question My Chatbot Handled Poorly

### Query: "What are the risks of a PET scan?"

**Actual system response:**
The provided context does not mention the risks of a PET scan. The context only discusses MRI scans and CT scans, but does not provide information about PET scans. Therefore, I cannot provide an answer to this question based on the given context.

**Sources cited:**
- https://i-med.com.au/procedures/mri-scan
- https://i-med.com.au/procedures/ct-scan

**What went wrong:** This is a **retrieval problem**. PET scan was not one of the procedures I scraped, so there is no PET scan content in my vector store. However, the retrieval system still returned the closest matching chunks (MRI and CT scan pages) and passed them to the LLM. The LLM correctly refused to fabricate an answer, but it still cited irrelevant source URLs which is misleading, a patient might visit those pages expecting PET scan risk information and find none.

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
This was a conscious decision, I preserved this behaviour as an honest example of a retrieval limitation rather than masking it.

---

## Q3: Things a Patient Would Ask That My Chatbot Cannot Answer

**1. "How much does a knee MRI cost at I-MED?"**
**Gap type: (a) Data does not exist on the website**
The website explicitly states fees vary and will be advised at time of booking. No specific pricing is published. Confirmed by Action Step 1 — the accounts team replied that they cannot provide quotes via email and redirected me to contact a local clinic directly. My chatbot handles this gracefully, when asked "How much does an MRI cost?" it responds:

> "The cost of an MRI is not explicitly stated in the provided context. To get an accurate answer, I would advise you to contact your local I-MED clinic directly by visiting i-med.com.au/find-a-radiology-clinic."

This behaviour was implemented after receiving the email reply in Action Step 1, by updating the system prompt to always redirect pricing questions to the clinic finder page.

**2. "What are the opening hours of the I-MED clinic in Parramatta?"**
**Gap type: (a) Data does not exist in my scraped dataset**
My scraper successfully extracted clinic names, addresses, and phone numbers from the clinic finder page (server-rendered HTML). However, opening hours are not shown on the main listings page, they appear only on each clinic’s “View clinic information” detail page.
Since I did not scrape those individual clinic pages, the chatbot cannot answer opening-hours questions. This could be fixed by extending the scraper to follow each clinic detail link and extract opening hours.

**3. "What are the risks of a PET scan?"**
**Gap type: (a) Data does not exist in my scraped dataset**
PET scan was not included in the 7 procedures I scraped. The website does have a PET scan page, but I did not scrape it. This is a coverage gap in my dataset rather than a website limitation — it could be fixed by adding the PET scan URL to the scraper.

---

## Q4: CT Scan Chunking Analysis

The CT scan page at i-med.com.au/procedures/ct-scan produced **8 chunks** after scraping and embedding.

===== Chunk 0 =====

> Computed tomography - CT scan A CT scan uses sophisticated x-ray technology to take images of parts of the body in very fine slices. The fine detail allows accurate diagnosis of a variety of illnesses and injuries. Computed tomography - CT scan A CT scan uses sophisticated x-ray technology to take images of parts of the body in very fine slices. The fine detail allows accurate diagnosis of a variety of illnesses and injuries. What is a CT scan? Computed tomography is commonly referred to as a ‘CT scan’. It is a way of using x-rays to take pictures or images in very fine slices through the part of the body that the doctor has asked to be investigated. One way to think of it is of taking slices through a loaf of bread, with more slices providing increasingly detailed images. The most recent machines are multi-slice (MSCT) scanners, producing up to 320 slices that are often less than 1mm thick. Once the radiographer has taken the scan, these very thin slices can be put all together to reconstruct the loaf (or in this case your body). Once they are put back together the radiographer can cut it into the slices that will help the radiologist (a doctor who has specialised in diagnostic imaging) to see the parts of the body that are of interest. With all of these different slices and 3D reconstructions, the radiologist will have a very detailed picture of the structures making up your body. This should help them to make a diagnosis so that the right treatment can be planned as soon as possible. Safe radiation dose management Our commitment to your safety is our highest priority. I-MED Radiology invests time, effort and resources into making sure that every patient receives a quality medical imaging service utilising the most appropriate imaging techniques and the lowest possible dose of radiation. Our radiology staff are highly skilled technicians who are licensed to operate our modern diagnostic imaging equipment. They also actively participate in ongoing training and a process of continuous improvement to ensure our high safety and quality standards are maintained. We have implemented a radiation-dose-monitoring software solution (DOSE) in 208 CT, PET and SPECT systems across our Network. This innovative software is designed to optimise how we monitor, evaluate and report radiation doses — reinforcing our commitment to patient safety, data accuracy and clinical excellence. I-MED

================================================================================

===== Chunk 1 =====

> quality standards are maintained. We have implemented a radiation-dose-monitoring software solution (DOSE) in 208 CT, PET and SPECT systems across our Network. This innovative software is designed to optimise how we monitor, evaluate and report radiation doses — reinforcing our commitment to patient safety, data accuracy and clinical excellence. I-MED is proud to be the first to adopt Qaelum’s cutting-edge technology, DOSE , in the Australasian region. Book an appointment Book an appointment print Print this page print Print this page What to expect during a CT scan Do you speak a language other than English? You can watch this video using translated subtitles - follow these instructions to select your language. How much will my procedure cost? Fees for radiology procedures vary and depend on a number of factors, including the type of procedure, what has been requested on your referral and the Medicare rebates available. We will advise you of any fees associated with your examination at the time of making your appointment or when you arrive at the clinic. Alternatively you can contact us and one of our team will be happy to answer any queries regarding fees. For more information about fees and rebates please visit our account FAQs. I-MED CT scan locations keyboard_arrow_down Find a complete list of I-MED Radiology clinics offering CT scanning here How do I prepare for a CT scan? keyboard_arrow_down If necessary, our clinic will provide you with instructions for your CT scan prior to your appointment. These instructions are very important as they may affect the accuracy of the test or require that the test be rebooked if you are not properly prepared for the CT scan. Some tests require no preparation, these include: brain, sinus or facial bones, temporal bones (inner ear), spine, knee or wrist, and CT scans of the bones. Many types of CT scan require an injection of an iodinated contrast material to show blood vessels and some organs. For these tests we will ask you to fast (not eat) prior to your appointment. It is important that the need to fast does not affect you if you have special dietary requirements (e.g. diabetes). Please check with your doctor or our clinic if you have any concerns. Chest CT preparation: Two hour fast Medication as normal Abdomen/pelvis CT & abdomen/pelvis + chest CT: Two hour fast Drink 1 litre of water, one hour before your appointment

================================================================================

===== Chunk 2 =====

> if you have special dietary requirements (e.g. diabetes). Please check with your doctor or our clinic if you have any concerns. Chest CT preparation: Two hour fast Medication as normal Abdomen/pelvis CT & abdomen/pelvis + chest CT: Two hour fast Drink 1 litre of water, one hour before your appointment time Can go to the bathroom, no need to hold bladder Medication as normal All patients are asked if they have kidney disease, diabetes or if taking metformin. If ‘yes’ to any of the above, ask patient to bring copies of recent blood tests (within the last 3 months) to their appointment. If you do require an iodinated contrast injection for your test, the radiologist or radiographer will discuss this with you. They will then use a needle to insert a cannula (a small plastic tube) into a vein in your arm or the back of your hand so that the iodine contrast can be inserted into the cannula during the test. While the iodinated contrast used for injections is considered very safe, there are precautions that must be taken when using it, particularly if you have poor kidney function or diabetes. Tests investigating your abdomen may require you to drink a different kind of iodinated contrast solution to outline your intestine (part of your digestive system). This will also require fasting. This drink is given in a different way depending where you are having the CT scan done. You will usually be asked to drink part of the whole dose an hour prior to the scanning time and the rest of it just before entering the scanning room. Depending on the type of scan that you are having you may be asked to change into a gown to avoid parts of your clothing affecting the scan. If you have any concerns regarding fasting, the iodinated contrast injection or your medication you should contact your own doctor or our clinic prior to your appointment. It is important to follow the instructions you are given to ensure that the test is done safely, accurately and efficiently and so that you do not need to have the scan rescheduled or repeated. What happens during a CT scan? keyboard_arrow_down CT scans are designed to look at specific parts of the body and are tailored for each person, to investigate their particular condition. This means that all CT scans are slightly different. The CT

================================================================================

===== Chunk 3 =====

> not need to have the scan rescheduled or repeated. What happens during a CT scan? keyboard_arrow_down CT scans are designed to look at specific parts of the body and are tailored for each person, to investigate their particular condition. This means that all CT scans are slightly different. The CT scan equipment is a large square machine with a circular hole, sometimes described as looking like a “donut”. The process involves you lying on a bed attached to the scanner (this may be feet first or head first depending on the part of the body being looked at). The bed will then be raised up to a height level with the circular hole in the scanner and the bed slides in and out of the hole several times while pictures are being taken. It is important to try not to move during the scan as it will affect the quality of the pictures and make them harder for the radiologist to interpret. The radiographer performing the CT scan may ask you to hold your breath for some scans. The length of time for each breath hold is usually under 10 seconds. Most scanners in use now are able to give instructions in different languages to help you understand what you need to do and what is happening. They will also often have ways of communicating with you if your hearing is poor. The first few scans are usually done to set up the machine ready for the test. When the test is programmed into the computer by the radiographer and the scan is ready to go, they may remind you to keep still. If your test requires an iodinated contrast injection, the radiographer will come into the room to administer it using either a hand held syringe or a mechanical pump. The pump helps to put the iodinated contrast in at a set rate and allows for the scanner to target specific areas of the body. When the iodinated contrast is injected, most people will get a strange metallic taste in the mouth and feel a warm sensation through the body. This warm sensation may concentrate around the groin or buttock region and can feel like you may have wet yourself, even though you have not. Do not be concerned if this happens, it is a common sensation and usually goes away within a couple of minutes. Once the radiographer

================================================================================

===== Chunk 4 =====

> body. This warm sensation may concentrate around the groin or buttock region and can feel like you may have wet yourself, even though you have not. Do not be concerned if this happens, it is a common sensation and usually goes away within a couple of minutes. Once the radiographer has reviewed the images briefly to check that the appropriate areas have been shown, they will come into the room to help you off the bed. The radiographer will not be able to give you any results after the CT scan; this is the responsibility of your doctor and the radiologist who interprets the images from the scan and provides a report to your doctor. Once the CT scan is completed, you will have the cannula removed so you can go home. How long does a CT scan take? keyboard_arrow_down The time taken to complete the CT scan will vary, depending on the examination that has been requested by your referring doctor. CT scans that do not require an injection and are usually quite quick and may be completed within 5 minutes. In the case of CT scans which require you to drink a contrast solution or have an injection, the preparation time is often much longer than that of the scan itself. When a drink is required for an abdominal scan (of your stomach), you are often asked to have that drink an hour before the appointment time. This may be done prior to you arriving at the hospital or radiology practice or while you are in the waiting area. Even when you are having a CT scan that requires an injection or a drink and other preparation, the time taken for the scan is usually under ten minutes. What are the benefits of a CT scan? keyboard_arrow_down CT scans are a fast, effective and accurate way of assisting your doctor to make a diagnosis and treat your condition. Are there any after effects from a CT scan? keyboard_arrow_down The vast majority of people who have a CT scan have no after effects at all. After the test, you should be able to eat and drink as normal and resume regular activities. If you have an injection of iodinated contrast, the sensations of warmth and the strange taste usually experienced should go away within a few minutes. In very uncommon cases, some people may be allergic to the iodinated

================================================================================

===== Chunk 5 =====

> should be able to eat and drink as normal and resume regular activities. If you have an injection of iodinated contrast, the sensations of warmth and the strange taste usually experienced should go away within a few minutes. In very uncommon cases, some people may be allergic to the iodinated contrast given into the vein in your arm or the back of your hand. It is not possible to predict if a person will be allergic to the iodinated contrast, though our staff are well trained to deal with allergic reactions should they arise. It is important to make the radiographer aware of any other allergies that you may have, prior to having the injection. People who are allergic to the iodinated contrast used in CT scans may get some of the following symptoms: Gagging or feeling of suffocation or swelling of the inside of the throat or mouth Dizziness and/or headache Sneezing and/or watering eyes Itching A skin rash or hives Nausea and/or vomiting Change in blood pressure If you do feel any of these symptoms after your CT scan, it is important to tell the radiographer immediately. If these feelings come on after leaving the clinic, you should return immediately (if close by), or attend the nearest doctor or emergency department. What are the risks of a CT scan? keyboard_arrow_down Radiation exposure: As is the case with most tests and medications prescribed by your doctor, CT does have risks that cannot be avoided. Our staff are highly trained to minimise these risks by using the lowest possible radiation dose to achieve quality images that allow the radiologist to make an accurate diagnosis. The radiographer will only scan the part(s) of the body required, and do their best to avoid scanning areas that are particularly sensitive to radiation - this may involve the use of shields made of lead or bismuth (a type of metallic substance). A CT scanner uses x-rays to obtain the pictures required for the radiologist to make a diagnosis. As is commonly known, x-rays are a form of radiation and must be used carefully by trained professionals to decrease the risks involved. These risks are: A very small increase in the risk of developing cancer later in life. This low risk is considered to be outweighed by the benefits provided by the scan. Risk to an unborn child if you are pregnant. This risk could

================================================================================

===== Chunk 6 =====

> trained professionals to decrease the risks involved. These risks are: A very small increase in the risk of developing cancer later in life. This low risk is considered to be outweighed by the benefits provided by the scan. Risk to an unborn child if you are pregnant. This risk could take the form of a very small increase in the risk of cancer or a malformation if you are exposed to radiation during the first months of your pregnancy. Minimising risks from radiation include making sure that every CT scanner in use is regularly maintained and calibrated (tested and set to ensure accuracy) by specialised technicians. This is required by State and Federal laws. How do I get my results? keyboard_arrow_down Your doctor will receive a written report on your test as soon as is practicable. It is very important that you discuss the results with the doctor who referred you so they can explain what the results mean for you. Safety information for diabetics keyboard_arrow_down Product information for diabetic sensors (CGM) and insulin pumps indicate the potential for malfunction if directly exposed to x-rays. Please notify staff of any diabetic equipment attached to you prior to your procedure/appointment. You MAY be asked to remove or disconnect the device prior to the exam, or more closely monitor their performance/accuracy after the exam. Related procedures CT Colonography CT Coronary Angiography Scan (CTCA) Coronary artery calcium scoring Dynamic 4D CT CT Lung Ventilation Analysis Software (CTLVAS)™ scan CT lung biopsy This information has been reviewed and approved by Dr Ronald Shnier (I-MED Chief Medical Officer). Related articles CT scan 101: everything you need to know A collection of important resources for patients needing a CT scan. At I-MED Radiology, we’re committed to finding answers, helping your doc ... Read more Why I-MED Radiology At I-MED Radiology, when you need answers, we are here to provide the highest quality care and deliver the most accurate diagnostic outcomes ... Read more Book an appointment Book an appointment print Print this page Related procedures CT Colonography CT Coronary Angiography Scan (CTCA) Coronary artery calcium scoring Dynamic 4D CT CT Lung Ventilation Analysis Software (CTLVAS)™ scan CT lung biopsy This information has been reviewed and approved by Dr Ronald Shnier (I-MED Chief Medical Officer). How much will my procedure cost? Fees for radiology procedures vary and depend on a number of factors, including the type of

================================================================================

===== Chunk 7 =====

> Dynamic 4D CT CT Lung Ventilation Analysis Software (CTLVAS)™ scan CT lung biopsy This information has been reviewed and approved by Dr Ronald Shnier (I-MED Chief Medical Officer). How much will my procedure cost? Fees for radiology procedures vary and depend on a number of factors, including the type of procedure, what has been requested on your referral and the Medicare rebates available. We will advise you of any fees associated with your examination at the time of making your appointment or when you arrive at the clinic. Alternatively you can contact us and one of our team will be happy to answer any queries regarding fees. For more information about fees and rebates please visit our account FAQs. Related articles CT scan 101: everything you need to know A collection of important resources for patients needing a CT scan. At I-MED Radiology, we’re committed to finding answers, helping your doc ... Read more Why I-MED Radiology At I-MED Radiology, when you need answers, we are here to provide the highest quality care and deliver the most accurate diagnostic outcomes ... Read more

================================================================================

The brain, chest and abdomen/pelvis preparation instructions are primarily located in Chunks 1, but the abdomen/pelvis preparation details and few chest details continue into Chunk 2. Therefore, they are not cleanly separated into distinct semantic chunks, nor are they fully contained within a single chunk, they span adjacent chunks due to fixed word-count chunking.

**Query: "Do I need to fast before a chest CT scan?"**

**Actual system response:**
According to the CT Scan procedure on the I-MED Radiology website, for a Chest CT preparation, you are required to fast for 2 hours before the appointment, and you should take your medication as normal.

**Source:** https://i-med.com.au/procedures/ct-scan

**Assessment:** In this case, the chatbot performed correctly because the fasting instruction for Chest CT was clearly present in one of the top-ranked chunks retrieved by semantic search. However, this success is dependent on how chunk boundaries align with the page layout. Since preparation instructions span adjacent chunks, a different chunk size or longer page could result in partial retrieval or incomplete instructions. This highlights a structural limitation of fixed word-count chunking.

A more robust production approach would:

First split content by semantic HTML headings.

Then apply token-based chunking within each section.

Ensure each preparation subtype remains self-contained within a retrieval unit.