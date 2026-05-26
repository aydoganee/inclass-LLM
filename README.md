# InClass LLM Platform

GROUP-12


A FastAPI-based backend for the InClass LLM Platform.

## Setup

1. **Clone the repository**

   ```bash
   git clone <repo-url>
   cd inclass-llm
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   ```bash
   cp .env.example .env
   ```

   Fill in the values in `.env`:
   - `SUPABASE_URL` — your Supabase project URL
   - `SUPABASE_SERVICE_ROLE_KEY` — your Supabase service role key
   - `DATABASE_URL` — your PostgreSQL connection string
   - `OPENROUTER_API_KEY` — your OpenRouter API key

5. **Run the development server**

   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`.

## Running Tests

```bash
 python -m uvicorn app.main:app --reload
```
# inclass-LLM
