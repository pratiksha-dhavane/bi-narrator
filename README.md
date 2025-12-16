# BI Narrator – Generative AI for Executive BI Narratives

## Overview

BI Narrator is a Generative AI–powered application that converts structured business data (CSV) into **factual, audit-ready executive summaries and narratives**. The system is designed to avoid hallucinations by separating **deterministic analytics** from **controlled LLM-based narration**.

This project focuses on **accuracy, reproducibility, and explainability**, making it suitable for BI and analytics use cases where trust in numbers is critical.

---

## Key Features

* Upload CSV data and select relevant columns (date, metric, optional category)
* Deterministic analytics layer for:

  * Time-based aggregation
  * KPI computation (total, growth, trend direction, volatility)
  * Peak and trough identification
  * Category contribution analysis
* Strictly constrained LLM prompting to ensure:

  * No hallucinated numbers
  * No invented insights or causes
  * Audit-ready, factual narratives
* Interactive Streamlit UI
* Deployable on Streamlit Cloud

---

## Architecture (High Level)

1. **Input Layer**

   * CSV file upload
   * User-selected columns (date, metric, category)

2. **Analytics Layer (Deterministic)**

   * Data cleaning and validation
   * Time-series aggregation
   * KPI and contribution computation

3. **Prompt Formatting Layer**

   * Injects pre-computed analytics into a strict prompt template
   * Enforces output structure and behavioral constraints

4. **LLM Layer**

   * Uses Gemini API
   * Generates executive summary and narrative strictly from provided facts

5. **UI Layer (Streamlit)**

   * Displays generated narrative
   * Handles user input and validation

---

## Tech Stack

* **Python**
* **Pandas / NumPy** – analytics and aggregation
* **Streamlit** – user interface and deployment
* **Gemini API** – narrative generation
* **Prompt Engineering** – hallucination control and structure enforcement

---

## How to Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/pratiksha-dhavane/bi-narrator.git
cd bi-narrator
```

### 2. Create and activate a virtual environment (recommended)

```bash
conda create -n bi-narrator python=3.11
conda activate bi-narrator
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set environment variable

Create a `.env` file **(local only)**:

```env
GEMINI_API_KEY=your_api_key_here
```

Or export it directly:

```bash
export GEMINI_API_KEY=your_api_key_here
```

### 5. Run the app

```bash
streamlit run app.py
```

---

## Using the Application

1. Upload a CSV file
2. Select:

   * Date column (must be parseable as dates)
   * Metric column (must be numeric)
   * Category column (optional)
3. Enter audience and tone (free text)
4. Click **Generate Narrative**
5. Review the executive summary and narrative

---

## Design Principles

* **No hallucinations**: The LLM never computes numbers
* **Deterministic analytics**: All KPIs are calculated in Python
* **Strict prompt control**: The model is constrained to factual output
* **Auditability**: Every sentence maps back to provided data

---

## Deployment (Streamlit Cloud)

1. Push the repository to GitHub
2. Create a Streamlit Cloud app pointing to `app.py`
3. Add the following secret in Streamlit settings:

```toml
GEMINI_API_KEY = "your_api_key_here"
```

4. Deploy

---

## Limitations

* Currently supports CSV files only
* Assumes clean, well-structured input data
* Narrative style is intentionally conservative and factual

---

## Future Improvements

* Excel file support
* Relaxed / executive-friendly narrative mode
* Additional KPIs and visualizations
* Model-agnostic LLM interface

---

## Author

**Pratiksha Dhavane**
Personal Generative AI Project
