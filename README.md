# Retrieval-Ready Study Assistant for NCERT Science

A bounded study assistant for NCERT Class 9 Science (Chapter 6 — How Forces Affect Motion), built for the PariShiksha edtech pilot. The system extracts, chunks, and retrieves textbook content using BM25, then generates grounded answers via a local LLM (phi3 via Ollama).

---

## Project Structure

```
retrieval-study-assistant/
├── README.md
├── requirements.txt
├── main.py                    # answer(question) → (answer, chunks)
├── evaluation.py              # automated evaluation runner
├── evaluation_results.md      # 20-question evaluation table
├── reflection.md              # reflection questionnaire
├── notebook.ipynb             # end-to-end runnable notebook
├── src/
│   ├── chunking/
│   │   ├── chunker.py         # sentence-based chunking with overlap
│   │   └── tokenizer.py      # GPT-2 / BERT / T5 tokenizer comparison
│   ├── extraction/
│   │   ├── pdf_loader.py      # PDF text extraction
│   │   └── clean_text.py     # text cleaning pipeline
│   ├── generation/
│   │   └── llm.py            # Ollama-based LLM generation with grounding prompt
│   └── retrieval/
│       └── bm25.py           # BM25Okapi retriever
└── Data/
    └── Raw/                   # place your NCERT PDF here (not committed)
```

---

## Data Source

**NCERT Class 9 Science — Chapter 6 (How Forces Affect Motion)**  
Official source: [https://ncert.nic.in/textbook.php?iesc1=0-11](https://ncert.nic.in/textbook.php?iesc1=0-11)  
Direct chapter file: `iesc106.pdf`

> **Do not commit the PDF to the repository.** Download it from the NCERT website and place it at `Data/Raw/iesc106.pdf`.

---

## Setup Instructions

### 1. Prerequisites

- Python 3.10 or newer
- [Ollama](https://ollama.com/) installed and running locally
- ~2 GB free disk space

### 2. Clone the repository

```bash
git clone https://github.com/hiten4/retrieval-study-assistant.git
cd retrieval-study-assistant
```

### 3. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Pull the LLM model via Ollama

```bash
ollama pull phi3
```

### 6. Download the NCERT PDF

Download Chapter 6 from [https://ncert.nic.in/textbook.php?iesc1=0-11](https://ncert.nic.in/textbook.php?iesc1=0-11) and place it at:

```
Data/Raw/iesc106.pdf
```

---

## Running the Project

### Run the end-to-end notebook

```bash
jupyter notebook notebook.ipynb
```

Run all cells top-to-bottom. The notebook covers all four stages: corpus extraction, retrieval, generation, and evaluation.

### Run evaluation only

```bash
python evaluation.py
```

This runs 20 questions through the pipeline and saves results to `evaluation_results.md`.

### Interactive single-question mode

Uncomment the interactive loop at the bottom of `main.py` and run:

```bash
python main.py
```

---

## System Overview

| Stage | Component | Description |
|-------|-----------|-------------|
| 1 | `pdf_loader.py` | Extracts raw text from NCERT PDF |
| 1 | `clean_text.py` | Removes noise, normalises whitespace |
| 1 | `chunker.py` | Sentence-aware chunking (size=300, overlap=50) |
| 1 | `tokenizer.py` | Compares GPT-2, BERT, T5 tokenizers |
| 2 | `bm25.py` | BM25Okapi retriever, returns top-k chunks |
| 3 | `llm.py` | phi3 via Ollama, grounding prompt enforced |
| 4 | `evaluation.py` | 20-question eval with correctness / grounding / refusal |

---

## Corpus

- **Chapter**: How Forces Affect Motion (NCERT Class 9 Science)
- **Content types**: Conceptual explanations, worked examples, end-of-chapter questions
- **Chunking**: 300-word window, 50-word sentence-aligned overlap

---

## Evaluation Summary

| Metric | Count / 20 |
|--------|-----------|
| Correct answers | 11 |
| Grounded answers | 11 |
| Appropriate refusals (out-of-scope) | 2 |

See `evaluation_results.md` for the full table and failure analysis.

---

## Known Limitations

- Local Ollama + phi3 required; no cloud API fallback in current build
- Grounding is inconsistent due to PDF extraction noise (digit removal bug, figure captions mixed into body text)
- Out-of-scope refusals partially work — model sometimes explains it cannot answer rather than giving a clean refusal signal
- Dense retrieval (embeddings) not yet implemented — BM25 only

---

## Backup Corpus

If `ncert.nic.in` is unreachable, use:  
OpenStax College Physics (CC-BY): [https://github.com/philschatz/physics-book](https://github.com/philschatz/physics-book)
