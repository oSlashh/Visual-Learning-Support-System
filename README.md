# SmartNotes AI - B.Tech Major Project

SmartNotes AI is an AI-powered study companion designed to transform lecture PDFs into concise summaries, key terms, and interactive flashcards.

## Project Structure

```text
SmartNotesAI/
├── frontend/             # Angular Standalone SPA Frontend
│   ├── src/
│   ├── angular.json
│   └── package.json
├── backend/              # Flask Web API Backend
│   ├── routes/           # Blueprints and endpoints
│   ├── modules/          # Core Python NLP modules
│   ├── uploads/          # Temporary PDF file storage
│   ├── requirements.txt  # Python package list
│   └── app.py            # Flask entry point
├── README.md
└── .gitignore
```

## Running the Application

### 1. Python Flask Backend
Navigate to the `backend/` directory:
1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
2. Activate the virtual environment:
   * **Windows**: `venv\Scripts\activate`
   * **macOS/Linux**: `source venv/bin/activate`
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the server:
   ```bash
   python app.py
   ```
The backend server runs on `http://localhost:5000`.

### 2. Angular Frontend
Navigate to the `frontend/` directory:
1. Install dependencies:
   ```bash
   npm install
   ```
2. Run the development server:
   ```bash
   npm start
   ```
Open `http://localhost:4200` in your browser.
