"""FastAPI application with /check and /rephrase endpoints."""
import io

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.config import get_enabled_services, get_openai_config, load_config
from backend.models import CheckResponse, RephraseResponse, ServiceResult
from backend.services.ai_detector import detect_all_ai_services
from backend.services.plagiarism import check_all_plagiarism_services
from backend.services.rephraser import rephrase_with_first_enabled
from backend.services.summarizer import generate_summary
from backend.utils.pdf_parser import extract_text_from_pdf

app = FastAPI(
    title="Plagiarism Checker API",
    description="API for plagiarism checking, AI content detection, and text rephrasing",
    version="1.0.0"
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
async def root():
    """Serve the frontend HTML page."""
    return FileResponse("frontend/index.html")


@app.post("/check", response_model=CheckResponse)
async def check_text(
    text: str | None = Form(None),
    file: UploadFile | None = File(None)
) -> CheckResponse:
    """Check text for plagiarism and AI-generated content.
    
    Accepts text content or a PDF file. Runs all enabled plagiarism and AI
    detection services, then generates a human-friendly summary using OpenAI.
    
    Args:
        text: Text content to check (optional if file is provided).
        file: PDF file to extract text from (optional if text is provided).
    
    Returns:
        CheckResponse with summary and detailed results.
    
    Raises:
        HTTPException: If no text or file is provided, or if text extraction fails.
    """
    # Extract text from PDF if file is provided
    if file is not None:
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported"
            )
        try:
            content = await file.read()
            text = extract_text_from_pdf(io.BytesIO(content))
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    if not text or not text.strip():
        raise HTTPException(
            status_code=400,
            detail="No text provided. Please provide text or upload a PDF file."
        )
    
    # Load configuration
    try:
        config = load_config()
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Get enabled services
    plagiarism_services = get_enabled_services(config, "plagiarism_checkers")
    ai_detector_services = get_enabled_services(config, "ai_detectors")
    openai_config = get_openai_config(config)
    
    # Run all checks
    plagiarism_results = await check_all_plagiarism_services(text, plagiarism_services)
    ai_detection_results = await detect_all_ai_services(text, ai_detector_services)
    
    # Generate summary
    summary = await generate_summary(
        text=text,
        plagiarism_results=plagiarism_results,
        ai_detection_results=ai_detection_results,
        openai_api_key=openai_config["api_key"],
        openai_model=openai_config["model"]
    )
    
    return CheckResponse(
        summary=summary,
        plagiarism_results=plagiarism_results,
        ai_detection_results=ai_detection_results,
        original_text=text
    )


@app.post("/rephrase", response_model=RephraseResponse)
async def rephrase_text(
    text: str = Form(...)
) -> RephraseResponse:
    """Rephrase text and run all checks on the improved version.
    
    Sends text to a rephrasing service, then runs plagiarism and AI detection
    on the rephrased text, and generates a new summary.
    
    Args:
        text: Original text content to rephrase.
    
    Returns:
        RephraseResponse with rephrased text, summary, and detailed results.
    
    Raises:
        HTTPException: If no text is provided or if rephrasing fails.
    """
    if not text or not text.strip():
        raise HTTPException(
            status_code=400,
            detail="No text provided for rephrasing."
        )
    
    # Load configuration
    try:
        config = load_config()
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Get enabled services
    rephrasing_services = get_enabled_services(config, "rephrasing")
    plagiarism_services = get_enabled_services(config, "plagiarism_checkers")
    ai_detector_services = get_enabled_services(config, "ai_detectors")
    openai_config = get_openai_config(config)
    
    # Rephrase the text
    rephrased_text, rephrase_result = await rephrase_with_first_enabled(
        text, rephrasing_services
    )
    
    if not rephrase_result.success:
        raise HTTPException(
            status_code=500,
            detail=f"Rephrasing failed: {rephrase_result.error}"
        )
    
    if not rephrased_text:
        raise HTTPException(
            status_code=500,
            detail="Rephrasing returned empty text"
        )
    
    # Run all checks on rephrased text
    plagiarism_results = await check_all_plagiarism_services(rephrased_text, plagiarism_services)
    ai_detection_results = await detect_all_ai_services(rephrased_text, ai_detector_services)
    
    # Generate summary for rephrased text
    summary = await generate_summary(
        text=rephrased_text,
        plagiarism_results=plagiarism_results,
        ai_detection_results=ai_detection_results,
        openai_api_key=openai_config["api_key"],
        openai_model=openai_config["model"]
    )
    
    return RephraseResponse(
        summary=summary,
        rephrased_text=rephrased_text,
        plagiarism_results=plagiarism_results,
        ai_detection_results=ai_detection_results,
        original_text=text
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
