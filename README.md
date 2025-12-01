# Plagiarism Checker MVP

A complete web application for plagiarism checking with AI content detection and optional rephrasing functionality.

## Features

- **Text Input**: Paste text directly or upload a PDF file
- **Plagiarism Detection**: Check text against multiple plagiarism detection services
- **AI Content Detection**: Identify AI-generated content using multiple detection services
- **AI-Powered Summary**: Get a human-friendly summary of results powered by OpenAI
- **Text Rephrasing**: Rephrase text to make it more original, then re-run all checks

## Project Structure

```
├── backend/
│   ├── main.py                 # FastAPI application with /check and /rephrase endpoints
│   ├── config.py               # Configuration loader
│   ├── models.py               # Pydantic models for requests/responses
│   ├── services/
│   │   ├── __init__.py
│   │   ├── plagiarism.py       # Plagiarism check service caller
│   │   ├── ai_detector.py      # AI content detection service caller
│   │   ├── rephraser.py        # Text rephrasing service caller
│   │   └── summarizer.py       # OpenAI summary generation
│   └── utils/
│       ├── __init__.py
│       └── pdf_parser.py       # PDF text extraction
├── frontend/
│   ├── index.html              # Main page
│   ├── style.css               # Styling
│   └── script.js               # Frontend logic
├── config/
│   └── services.yaml           # External services configuration
├── requirements.txt            # Python dependencies
├── .env.example                # Example environment variables
├── .gitignore
└── README.md                   # This file
```

## Requirements

- Python 3.9+
- OpenAI API key (for summaries and rephrasing)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd aiplaegcheck
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=your-openai-api-key-here
```

### 5. Configure External Services

Edit `config/services.yaml` to enable and configure your external services:

```yaml
services:
  plagiarism_checkers:
    - name: "Your Plagiarism Service"
      api_url: "https://api.example.com/check"
      api_key: "your-api-key"
      enabled: true

  ai_detectors:
    - name: "Your AI Detector"
      api_url: "https://api.example.com/detect"
      api_key: "your-api-key"
      enabled: true

  rephrasing:
    - name: "OpenAI Rephraser"
      api_url: "openai"  # Special value to use OpenAI for rephrasing
      api_key: ""        # Uses OPENAI_API_KEY from environment
      enabled: true

openai:
  api_key: "${OPENAI_API_KEY}"  # References environment variable
  model: "gpt-4"
```

### 6. Run the Application

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Open your browser and navigate to `http://localhost:8000`

## API Documentation

### POST `/check`

Check text for plagiarism and AI-generated content.

**Request:**
- Content-Type: `multipart/form-data`
- Parameters:
  - `text` (optional): Text content to check
  - `file` (optional): PDF file to upload

**Response:**
```json
{
  "summary": "Human-friendly summary of all results",
  "plagiarism_results": [
    {
      "service_name": "Service Name",
      "service_type": "plagiarism",
      "success": true,
      "result": {},
      "error": null
    }
  ],
  "ai_detection_results": [
    {
      "service_name": "Service Name",
      "service_type": "ai_detection",
      "success": true,
      "result": {},
      "error": null
    }
  ],
  "original_text": "The text that was checked"
}
```

### POST `/rephrase`

Rephrase text and run all checks on the improved version.

**Request:**
- Content-Type: `multipart/form-data`
- Parameters:
  - `text` (required): Text content to rephrase

**Response:**
```json
{
  "summary": "Human-friendly summary of results for rephrased text",
  "rephrased_text": "The rephrased version of the text",
  "plagiarism_results": [],
  "ai_detection_results": [],
  "original_text": "The original text before rephrasing"
}
```

### GET `/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Configuration

### Adding New Services

To add a new plagiarism checker, AI detector, or rephrasing service:

1. Open `config/services.yaml`
2. Add a new entry under the appropriate section:

```yaml
services:
  plagiarism_checkers:
    - name: "New Service Name"
      api_url: "https://api.newservice.com/check"
      api_key: "your-api-key"
      enabled: true
```

3. Restart the application

The system will automatically:
- Loop through all enabled services
- Skip disabled services
- Handle service failures gracefully
- Include results in the summary

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for summaries and rephrasing | Yes |
| `CONFIG_PATH` | Custom path to config file (default: `config/services.yaml`) | No |

## Development

### Running in Development Mode

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The `--reload` flag enables auto-reload when code changes are detected.

### API Documentation (Swagger)

When running, access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## License

MIT License
