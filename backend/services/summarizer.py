"""OpenAI summary generation service."""
from typing import Any

from openai import AsyncOpenAI

from backend.models import ServiceResult


async def generate_summary(
    text: str,
    plagiarism_results: list[ServiceResult],
    ai_detection_results: list[ServiceResult],
    openai_api_key: str,
    openai_model: str = "gpt-4"
) -> str:
    """Generate a human-friendly summary of check results using OpenAI.
    
    Args:
        text: The original text that was checked.
        plagiarism_results: Results from plagiarism checking services.
        ai_detection_results: Results from AI detection services.
        openai_api_key: OpenAI API key.
        openai_model: OpenAI model to use.
    
    Returns:
        Human-friendly summary string.
    """
    if not openai_api_key:
        return _generate_fallback_summary(plagiarism_results, ai_detection_results)
    
    try:
        client = AsyncOpenAI(api_key=openai_api_key)
        
        # Prepare context for OpenAI
        context = _prepare_results_context(text, plagiarism_results, ai_detection_results)
        
        response = await client.chat.completions.create(
            model=openai_model,
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert at analyzing plagiarism and AI detection results. 
                    Generate a clear, helpful summary for the user. Include:
                    1. How much plagiarism was found (percentage if available)
                    2. How much AI-generated content was detected
                    3. Which parts look suspicious (if identifiable)
                    4. What the user should do next (clear recommendations)
                    
                    Be concise but thorough. Use a friendly, helpful tone."""
                },
                {
                    "role": "user",
                    "content": context
                }
            ],
            temperature=0.5
        )
        
        return response.choices[0].message.content or _generate_fallback_summary(
            plagiarism_results, ai_detection_results
        )
    
    except Exception as e:
        # Fallback to basic summary if OpenAI fails
        return _generate_fallback_summary(plagiarism_results, ai_detection_results, str(e))


def _prepare_results_context(
    text: str,
    plagiarism_results: list[ServiceResult],
    ai_detection_results: list[ServiceResult]
) -> str:
    """Prepare context string for OpenAI summarization.
    
    Args:
        text: Original text (first 500 chars for context).
        plagiarism_results: Plagiarism check results.
        ai_detection_results: AI detection results.
    
    Returns:
        Formatted context string.
    """
    context_parts = [
        f"Text being analyzed (first 500 chars): {text[:500]}...\n\n"
    ]
    
    context_parts.append("PLAGIARISM CHECK RESULTS:\n")
    if plagiarism_results:
        for result in plagiarism_results:
            if result.success:
                context_parts.append(f"- {result.service_name}: {result.result}\n")
            else:
                context_parts.append(f"- {result.service_name}: Error - {result.error}\n")
    else:
        context_parts.append("- No plagiarism checkers were enabled or available.\n")
    
    context_parts.append("\nAI DETECTION RESULTS:\n")
    if ai_detection_results:
        for result in ai_detection_results:
            if result.success:
                context_parts.append(f"- {result.service_name}: {result.result}\n")
            else:
                context_parts.append(f"- {result.service_name}: Error - {result.error}\n")
    else:
        context_parts.append("- No AI detectors were enabled or available.\n")
    
    return "".join(context_parts)


def _generate_fallback_summary(
    plagiarism_results: list[ServiceResult],
    ai_detection_results: list[ServiceResult],
    error: str | None = None
) -> str:
    """Generate a basic fallback summary when OpenAI is unavailable.
    
    Args:
        plagiarism_results: Plagiarism check results.
        ai_detection_results: AI detection results.
        error: Optional error message to include.
    
    Returns:
        Basic summary string.
    """
    parts = ["## Analysis Summary\n\n"]
    
    if error:
        parts.append(f"*Note: AI summary generation encountered an issue: {error}*\n\n")
    
    # Plagiarism results
    parts.append("### Plagiarism Check\n")
    if plagiarism_results:
        successful = [r for r in plagiarism_results if r.success]
        failed = [r for r in plagiarism_results if not r.success]
        
        if successful:
            for result in successful:
                parts.append(f"- **{result.service_name}**: Check completed\n")
        if failed:
            for result in failed:
                parts.append(f"- **{result.service_name}**: {result.error}\n")
    else:
        parts.append("No plagiarism checkers were enabled.\n")
    
    # AI detection results
    parts.append("\n### AI Content Detection\n")
    if ai_detection_results:
        successful = [r for r in ai_detection_results if r.success]
        failed = [r for r in ai_detection_results if not r.success]
        
        if successful:
            for result in successful:
                parts.append(f"- **{result.service_name}**: Detection completed\n")
        if failed:
            for result in failed:
                parts.append(f"- **{result.service_name}**: {result.error}\n")
    else:
        parts.append("No AI detectors were enabled.\n")
    
    parts.append("\n### Recommendations\n")
    parts.append("Review the detailed results from each service to understand the analysis findings.\n")
    
    return "".join(parts)
