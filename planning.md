# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | CSUF CS Faculty directory | the official directory for csuf professors, could use to cross reference and see if professors exist even if there is no data on them from other sources| https://www.fullerton.edu/ecs/cs/faculty-staff/index.html |
| 2 | Doina Bein ratemyprofessor | ratemyprofessor reviews for Doina Bein | https://www.ratemyprofessors.com/professor/2239018 |
| 3 | Shawn Wang ratemyprofessor | ratemyprofessor reviews for Shawn Wang | https://www.ratemyprofessors.com/professor/2271552 |
| 4 | Sampson Akwafuo ratemyprofessor | ratemyprofessor reviews for Sampson Akwafuo| https://www.ratemyprofessors.com/professor/2723662 |
| 5 | Ning Chen ratemyprofessor | ratemyprofessor reviews for Ning Chen | https://www.ratemyprofessors.com/professor/867096 |
| 6 | James S. Choi ratemyprofessor | ratemyprofessor reviews for James Choi | https://www.ratemyprofessors.com/professor/133450 |
| 7 | Bin Cong ratemyprofessor | ratemyprofessor reviews for Bin Cong | https://www.ratemyprofessors.com/professor/57425 |
| 8 | Mikhail Gofman ratemyprofessor | ratemyprofessor reviews for Mikhail Gofman | https://www.ratemyprofessors.com/professor/1788308 |
| 9 | Wenlin Han ratemyprofessor | ratemyprofessor reviews for Wenlin Han | https://www.ratemyprofessors.com/professor/2384118 |
| 10 | Duy Ho ratemyprofessor | ratemrprofessor reviews for Duy Ho | https://www.ratemyprofessors.com/professor/3033207 |
| 11 | Floyd Holliday ratemyprofessor | ratemyprofessor reviews for Floyd Holliday | https://www.ratemyprofessors.com/professor/134276 |
| 12 | Paul Inventado ratemyprofessor | ratemyprofessor reviews for Paul Inventado| https://www.ratemyprofessors.com/professor/2331513 |
| 13 | Anli Ji ratemyprofessor | ratemyprofessor reviews for Anli Ji | https://www.ratemyprofessors.com/professor/3133350 | <!-- faculty directory lists her as "Annie Ji" -->
| 14 | Rong Jin ratemyprofessor | ratemyprofessor reviews for Rong Jin | https://www.ratemyprofessors.com/professor/2817717 |
| 15 | Chang-Hyun Jo ratemyprofessor | ratemyprofessor reviews for Chang-Hyun Jo | https://www.ratemyprofessors.com/professor/449937 |
| 16 | Mira Kim ratemyprofessor | ratemyprofessor reviews for Mira Kim | https://www.ratemyprofessors.com/professor/3024344 |
| 17 | Anand Panangadan ratemyprofessor | ratemyprofessor reviews for Anand Panangadan | https://www.ratemyprofessors.com/professor/2078580 |
| 18 | ASM Rizvi ratemyprofessor | ratemyprofessor reviews for ASM Rizvi | https://www.ratemyprofessors.com/professor/3114952 |
| 19 | Christopher Ryu ratemyprofessor | ratemyprofessor reviews for Christopher Ryu | https://www.ratemyprofessors.com/professor/2382378 |
| 20 | Michael Shafae ratemyprofessor | ratemyprofessor reviews for Michael Shafae | https://www.ratemyprofessors.com/professor/1133505 |
| 21 | Kanika Sood ratemyprofessor | ratemyprofessor reviews for Kanika Sood | https://www.ratemyprofessors.com/professor/2552839 |
| 22 | Yun Tian ratemyprofessor | ratemyprofessor reviews for Yun Tian | https://www.ratemyprofessors.com/professor/1981393 |
| 23 | Kevin Wortman ratemyprofessor | ratemyprofessor reviews for Kevin Wortman | https://www.ratemyprofessors.com/professor/1405066 |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->
**Chunk size:**
     split by review size
**Overlap:**
     none
**Reasoning:**
      Chunks will be chunked by review and have metadata for the review prepended as a header. This will prevent splitting of data that should be grouped together as a single review. This will not have a fixed character limit to prevent splitting of reviews if they don't fit nicely in the fixed limit. There will be no overlap because each review is already small enough to be a single chunk and should be kept separate as a natural boundary and separation of the data.
---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**
     all-MiniLM-L6-V2 
**Top-k:**
     8
**Production tradeoff reflection:**
     This embedding model will work well on no budget because it runs locally. There is no reason to use a multilingual embedding model, so the english only constraint is not a concern. The small chunk sizes of reviews are perfect for the miniLM which makes it favorable over more costly embedding models like BGE-large which has capabilities beyond what is needed for the scope of this project.
---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What do students say about Anand Panangadan's cpsc 481? | One student's ratemyprofessor review at https://www.ratemyprofessors.com/professor/2078580 claims he extends homework and projects, and another says he will answer questions with in depth explanations. both rated him with a Quality of 5.|
| 2 | Does Kanika Sood assign a lot of homework? | At https://www.ratemyprofessors.com/professor/2552839, one student on 2022-12-18 tagged their review with lots of homework, another did so on 2021-06-30.|
| 3 | how hard are Mira Kim's classes? | ratemyprofessor lists her average difficulty score as 2/5 at https://www.ratemyprofessors.com/professor/3024344|
| 4 | what are some complaints students have about Paul inventado?| At https://www.ratemyprofessors.com/professor/2331513, One student on 2018-05-20 claims that the midterm and final are difficult, another on 2018-05-24 claimed the projects were difficult. |
| 5 | How hard is Clark Kent's class? | Clark Kent is not a professor listed in the reference documents. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
