# 🌐 Q=NExUS: Autonomous Multi-Agent AI News Publisher

An enterprise-grade, fully automated AI media holding. This system autonomously scouts, edits, translates, and broadcasts tech and financial news across multiple Telegram channels in different languages (RU, EN, ES). Built with a focus on **Multi-Agent Orchestration, API Resilience, and Graceful Degradation**.

## 🚀 Key Architectural Achievements

This project demonstrates how to build an autonomous pipeline that survives rate limits, network drops, and LLM hallucinations.

### 1. Autonomous Multi-Agent Workflow (CrewAI)
* Utilizes `crewai` to orchestrate a team of specialized AI agents (Scouts, Writers, Editors).
* Agents autonomously search the web (`duckduckgo-search`), extract raw data from tech RSS feeds, and compile structured, highly engaging news drafts.

### 2. API Resilience & "Easter Egg" Fallback (Graceful Degradation)
* **The Problem:** Free-tier or highly active LLM APIs (Gemini, Groq) inevitably hit `429 Too Many Requests` limits, which usually crashes automated pipelines.
* **The Solution:** A robust fail-safe mechanism (`mr_cooper.py` and `nexus_sender.py`). If the LLM agents crash due to quota limits, the system intercepts the failure, halts the standard pipeline, and seamlessly broadcasts pre-written, localized "Easter Egg" interactive posts. This maintains channel engagement and hides technical downtime from the audience.

### 3. Multi-Lingual & Multi-Channel Broadcasting
* The publishing engine automatically translates the approved AI draft into English and Spanish.
* Integrates a custom graphics engine (`Pillow`) to dynamically fetch, brand (watermark), and attach images to the broadcasts via the Telegram API.

### 4. Automated Market Digests
* Uses `yfinance` to pull real-time market data (Crypto, S&P 500, Treasuries, Gold).
* Automatically calculates daily and monthly percentage changes, formats them with visual indicators, and publishes scheduled morning/evening financial briefs.

---

## 🛠️ Comprehensive Tech Stack

### 🧠 AI & Orchestration
* **CrewAI** - Multi-agent framework for assigning roles and tasks.
* **Google Gemini API / Groq API** - Core LLM brains for processing and translation.
* **LangChain** - Used for LLM integration and tool calling.

### 📡 Data Acquisition & Scraping
* **Feedparser** - RSS stream aggregation (TechCrunch, IEEE, SpaceNews, etc.).
* **DuckDuckGo Search (ddgs)** - Live web search capability for AI agents.
* **yfinance** - Real-time financial data extraction.

### ⚙️ Automation & Pipeline Control
* **Schedule** - Time-based execution routing.
* **Subprocess / Signal** - OS-level process management for the watchdog mechanisms.
* **Python-dotenv** - Secure credential and API key management (preventing secret leaks).

### 🗄️ Storage & Media
* **SQLite3** - Local database for archiving published news and preventing duplicate posts.
* **Pillow (PIL)** - Dynamic image processing and watermarking.

---

## 🗺️ Project Navigation Map (For Tech Reviewers)

* 📄 **`news_agency.py`** - The Agent Hub. Orchestrates the CrewAI logic and intercepts `429` LLM limits to write the `API_DEAD` emergency flag.
* 📄 **`nexus_sender.py`** - The Broadcaster. Handles multi-lingual distribution, image watermarking, and triggers the Interactive Easter Eggs if the AI fails.
* 📄 **`mr_cooper.py`** - The Watchdog. A custom fault-tolerant scheduler that monitors agent execution, handles timeouts, and enforces retry logic.
* 📄 **`digest_engine.py`** - The Financial Analyst. Pulls and calculates stock/crypto metrics.
* 📄 **`scraper.py`** - The Data Gatherer. Parses RSS feeds and filters out duplicate news using SQLite and historical text logs.