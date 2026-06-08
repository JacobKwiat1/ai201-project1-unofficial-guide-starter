# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

Student reviews of computer science professors at California State University, Fullerton. This knowledge is valuable because There are not many ways to accurately get information about what taking a class under a professor will be like. Students who have taken the class are the best possible source to find out. That information does exist in spaces online like ratemyprofessor, but accessing it can be inconvenient especially when you need to find and search through multiple professors as you're registering for classes. It requires reading through dozens of reviews of each professor to find what students have said about specific aspects of their teaching style, an AI tool can help to lighten that burden and streamline that information into quicker to digest chunks that are generated specifically to answer questions you are looking for.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Doina Bein | RateMyProfessors reviews | https://www.ratemyprofessors.com/professor/2239018 |
| 2 | Shawn Wang | RateMyProfessors reviews | https://www.ratemyprofessors.com/professor/2271552 |
| 3 | Sampson Akwafuo | RateMyProfessors reviews | https://www.ratemyprofessors.com/professor/2723662 |
| 4 | Ning Chen | RateMyProfessors reviews | https://www.ratemyprofessors.com/professor/867096 |
| 5 | James S. Choi | RateMyProfessors reviews | https://www.ratemyprofessors.com/professor/133450 |
| 6 | Bin Cong | RateMyProfessors reviews | https://www.ratemyprofessors.com/professor/57425 |
| 7 | Mikhail Gofman | RateMyProfessors reviews | https://www.ratemyprofessors.com/professor/1788308 |
| 8 | Wenlin Han | RateMyProfessors reviews | https://www.ratemyprofessors.com/professor/2384118 |
| 9 | Duy Ho | RateMyProfessors reviews | https://www.ratemyprofessors.com/professor/3033207 |
| 10 | Floyd Holliday | RateMyProfessors reviews | https://www.ratemyprofessors.com/professor/134276 |
| 11 | Paul Inventado | RateMyProfessors reviews | https://www.ratemyprofessors.com/professor/2331513 |
| 12 | Anli Ji | RateMyProfessors reviews | https://www.ratemyprofessors.com/professor/3133350 |
| 13 | Rong Jin | RateMyProfessors reviews | https://www.ratemyprofessors.com/professor/2817717 |
| 14 | Chang-Hyun Jo | RateMyProfessors reviews | https://www.ratemyprofessors.com/professor/449937 |
| 15 | Mira Kim | RateMyProfessors reviews | https://www.ratemyprofessors.com/professor/3024344 |
| 16 | Anand Panangadan | RateMyProfessors reviews | https://www.ratemyprofessors.com/professor/2078580 |
| 17 | ASM Rizvi | RateMyProfessors reviews | https://www.ratemyprofessors.com/professor/3114952 |
| 18 | Christopher Ryu | RateMyProfessors reviews | https://www.ratemyprofessors.com/professor/2382378 |
| 19 | Michael Shafae | RateMyProfessors reviews | https://www.ratemyprofessors.com/professor/1133505 |
| 20 | Kanika Sood | RateMyProfessors reviews | https://www.ratemyprofessors.com/professor/2552839 |
| 21 | Yun Tian | RateMyProfessors reviews | https://www.ratemyprofessors.com/professor/1981393 |
| 22 | Kevin Wortman | RateMyProfessors reviews | https://www.ratemyprofessors.com/professor/1405066 |

---

## Chunking Strategy

**Chunk size:** One chunk per review. The chunker imposes no fixed character limit of its own — it splits on review boundaries. The boundaries of the reviews are created as part of the scraper formatting. The scraper was also used to strip the HTML. and used to split the body into chunks. Reviews are naturally short because RateMyProfessors caps submitted reviews at ~350 characters, so every review fits comfortably in a single chunk and never needs to be split by a character count.

**Overlap:** None.

**Why these choices fit your documents:** Documents are chunked by review, with the review's metadata prepended as a header. This prevents splitting data that should be grouped together as a single review. Because RateMyProfessors already caps each review at ~350 characters, there is no need for the chunker to enforce its own character limit — splitting purely on review boundaries guarantees no review is ever cut in half. There is no overlap because each review is already small enough to be a single chunk and should be kept separate as a natural boundary and separation of the data.

**Final chunk count:** 779 chunks across 22 documents (757 review chunks + 22 per-professor summary chunks).

---

## Embedding Model

**Model used:** all-MiniLM-L6-v2 (via sentence-transformers). Retrieval returns the top-k = 8 chunks per query.

**Production tradeoff reflection:** This embedding model works well on no budget because it runs locally. There is no reason to use a multilingual embedding model, so the English-only constraint is not a concern. The small chunk sizes of reviews are perfect for MiniLM, which makes it favorable over more costly embedding models like BGE-large that has capabilities beyond what is needed for the scope of this project.

---

## Grounded Generation

**System prompt grounding instruction:** Grounding is enforced in two layers. First, the model is only shown the top-8 chunks returned by retrieval as context, so for a professor who is not in the documents there is simply no supporting text to answer from. Second, the system prompt explicitly constrains the model. It requires that the model only uses information found in the chunks given by the RAG. It was also specifically instructed to refuse to answer if it does not have adequate information in the sources. The generation temperature is also set to 0 to keep answers deterministic and reduce the model's tendency to embellish beyond the retrieved text.

**How source attribution is surfaced in the response:** Each retrieved chunk is formatted with a source tag before being passed to the model — `[i] Source: <professor> — <class> (review date) | <source URL>` — so every piece of evidence carries the RateMyProfessors URL it came from. The model is instructed to end its answer with a "Sources:" list of the URLs it actually used, and to omit that list entirely when it has no answer (as in the Clark Kent case). The GUI also displays a "Sources consulted" panel of URLs retrieved and a "Retrieved reviews" panel showing chunks the answer was grounded in, so a reader can verify each claim against its source.

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about Anand Panangadan's cpsc 481? | One student's ratemyprofessor review at https://www.ratemyprofessors.com/professor/2078580 claims he extends homework and projects, and another says he will answer questions with in depth explanations. both rated him with a Quality of 5. | Summarizes CPSC481 reviews: easy and fun, lenient on deadlines, caring, gives good feedback, and always open to answering questions. Cites the correct source URL (2078580). | Relevant | Accurate |
| 2 | Does Kanika Sood assign a lot of homework? | At https://www.ratemyprofessors.com/professor/2552839, one student on 2022-12-18 tagged their review with lots of homework, another did so on 2021-06-30. | Answers "yes," citing "lots of homework" tags and long, time-consuming assignments across CPSC313, CPSC332, and CPSC483. Cites the correct source URL (2552839). | Relevant | Accurate |
| 3 | how hard are Mira Kim's classes? | ratemyprofessor lists her average difficulty score as 2/5 at https://www.ratemyprofessors.com/professor/3024344 | Says her classes are easy and stress-free, and pulls the average difficulty of 2/5 from the professor summary chunk. Cites 3024344. | Partially relevant (5 of 8 retrieved chunks were Mira Kim incl. the summary; 3 drifted to Yun Tian, but were not used in the answer) | Accurate |
| 4 | what are some complaints students have about Paul inventado? | At https://www.ratemyprofessors.com/professor/2331513, One student on 2018-05-20 claims that the midterm and final are difficult, another on 2018-05-24 claimed the projects were difficult. | Lists complaints: disorganized grading, difficult midterm/final without a good background, and harder concepts covered quickly. Cites 2331513, but attributes all points to a single review and does not surface the "projects were difficult" complaint. | Relevant | Partially accurate |
| 5 | How hard is Clark Kent's class? | Clark Kent is not a professor listed in the reference documents. | Correctly refuses: "I don't have information about Clark Kent's class in the reviews," and lists no sources. | Off-target sources consulted and chunks retrieved are irrelevant to the prompt. All 8 are retrieved despite none being relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** "Is Kevin Wortman or Yun Tian a harder professor?" (a comparison question I tested outside the original five.)

**What the system returned:** "I don't have information about Kevin Wortman in the reviews. All the reviews provided are about Professor Yun Tian, describing her as a 'Tough Grader' and her classes as 'Test Heavy'." The system effectively answered for only one of the two professors and claimed it had nothing on the other — even though Kevin Wortman has 46 reviews in the corpus.

**Root cause (tied to a specific pipeline stage):** This is a retrieval-stage failure. A comparison question is embedded into a single query vector, and the similarity search returns the 8 globally-closest chunks regardless of which professor they belong to. The phrase "harder professor" sits semantically very close to Yun Tian's reviews (which are saturated with "Tough Grader," "Test Heavy," and "hard"), so all 8 retrieved slots were filled with Yun Tian chunks and zero Wortman chunks reached the prompt. When zero chunks about Wortman were gathered in the top-k, the model said that it had no information about him. I made sure this problem only appeared during comparison by testing a Wortman prompt which properly gathered chunks with data about him and responded appropriately.

**What you would change to fix it:** Detect when a query names more than one professor and retrieve per professor instead of once globally — run a separate top-k search for each name (or use ChromaDB's metadata `where` filter on the `professor` field), then concatenate the results so both sides are represented in the context. More generally, a single dense query vector cannot fairly represent a multi-entity question, so the retrieval stage needs to be entity-aware rather than relying on one global similarity ranking.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** The Chunking Strategy and Retrieval Approach sections were specific enough that implementation was close to a direct translation. It allowed me to be able to give the specs to claude and get a result extremely close to what I wanted. The Evaluation Plan also helped as it gave me a set of tests to use to test things. This helped catch bugs and building the evaluation plan for multiple cases helped me to be more intentional about what I test. One thing this helped catch was an issue where the response for a non-available professor still listed sources despite there being none.

**One way your implementation diverged from the spec, and why:** The spec described chunking only "by review," but during implementation I added a second chunk type — a per-professor summary chunk holding the overall stats (overall rating, average difficulty, would-take-again %). This was decided when reviewing responses for question 3 ("how hard are Mira Kim's classes?"), whose expected answer is the average difficulty of 2/5. To answer this well using the reviews would be just about impossible, but the source includes this information just outside of the reviews. I also added preprocessing the spec didn't mention (decoding HTML entities and removing duplicate reviews) after finding both in the scraped data.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* My Chunking Strategy section from planning.md and the format of the scraped review files, and asked it to implement the chunking stage.
- *What it produced:* A `chunking.py` module that splits each document into one chunk per review and attaches metadata, plus a per-professor summary chunk built from the file header.
- *What I changed or overrode:* I directed the specific metadata fields each chunk had to carry (source URL, professor, class, quality, difficulty, date, tags) and required that a summary chunk containing the file header be emitted for every professor, rather than only review chunks.

**Instance 2**

- *What I gave the AI:* My list of professor RateMyProfessors URLs from planning.md, and asked for a convenient way to scrape the review text into source documents.
- *What it produced:* It found that the reviews are not in the page's static HTML (RateMyProfessors is a React app) and instead queried the site's GraphQL API, producing a `scrape_rmp.py` that writes one formatted text file per professor into the documents folder.
- *What I changed or overrode:* I directed it to add the source URL to the top of each file so it could be carried into the chunk metadata and used for citations, and later had it pull in an additional professor (Anli Ji) once I added her link to the source table.
