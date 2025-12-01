"""Text rephrasing service caller."""
import os
from typing import Any

import httpx
from openai import AsyncOpenAI

from backend.models import ServiceResult


async def rephrase_text_with_openai(text: str, api_key: str) -> tuple[str, ServiceResult]:
    """Rephrase text using OpenAI.
    
    Args:
        text: Text content to rephrase.
        api_key: OpenAI API key.
    
    Returns:
        Tuple of (rephrased_text, ServiceResult).
    """
    try:
        client = AsyncOpenAI(api_key=api_key)
        
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional editor. Rephrase the following text to make it more original while preserving its meaning. Make it sound natural and human-written. Do not add any explanations, just provide the rephrased text."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.7
        )
        
        rephrased = response.choices[0].message.content or ""
        
        return rephrased, ServiceResult(
            service_name="OpenAI Rephraser",
            service_type="rephrasing",
            success=True,
            result={"rephrased_text": rephrased}
        )
    
    except Exception as e:
        return "", ServiceResult(
            service_name="OpenAI Rephraser",
            service_type="rephrasing",
            success=False,
            error=str(e)
        )


async def rephrase_text_with_service(
    text: str, 
    service_config: dict[str, Any]
) -> tuple[str, ServiceResult]:
    """Rephrase text using an external service.
    
    Args:
        text: Text content to rephrase.
        service_config: Service configuration with name, api_url, api_key.
    
    Returns:
        Tuple of (rephrased_text, ServiceResult).
    """
    service_name = service_config.get("name", "Unknown Service")
    api_url = service_config.get("api_url", "")
    api_key = service_config.get("api_key", "")
    
    # If api_url is "openai", use OpenAI rephrasing
    if api_url == "openai":
        openai_key = api_key or os.getenv("OPENAI_API_KEY", "")
        return await rephrase_text_with_openai(text, openai_key)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                api_url,
                json={"text": text},
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()
            result_data = response.json()
            
            # Extract rephrased text from response
            rephrased = result_data.get("rephrased_text", result_data.get("text", ""))
            
            return rephrased, ServiceResult(
                service_name=service_name,
                service_type="rephrasing",
                success=True,
                result=result_data
            )
    
    except httpx.TimeoutException:
        return "", ServiceResult(
            service_name=service_name,
            service_type="rephrasing",
            success=False,
            error="Request timed out"
        )
    except httpx.HTTPStatusError as e:
        return "", ServiceResult(
            service_name=service_name,
            service_type="rephrasing",
            success=False,
            error=f"HTTP error: {e.response.status_code}"
        )
    except Exception as e:
        return "", ServiceResult(
            service_name=service_name,
            service_type="rephrasing",
            success=False,
            error=str(e)
        )


async def rephrase_with_first_enabled(
    text: str, 
    services: list[dict[str, Any]]
) -> tuple[str, ServiceResult]:
    """Rephrase text using the first enabled rephrasing service.
    
    Args:
        text: Text content to rephrase.
        services: List of enabled rephrasing service configurations.
    
    Returns:
        Tuple of (rephrased_text, ServiceResult).
    """
    if not services:
        return "", ServiceResult(
            service_name="None",
            service_type="rephrasing",
            success=False,
            error="No rephrasing services enabled"
        )
    
    # Try each service until one succeeds
    last_result = None
    for service in services:
        rephrased, result = await rephrase_text_with_service(text, service)
        last_result = result
        if result.success:
            return rephrased, result
    
    # All services failed, return the last error
    if last_result is not None:
        return "", last_result
    
    # This should never happen since we check for empty services above
    return "", ServiceResult(
        service_name="None",
        service_type="rephrasing",
        success=False,
        error="No rephrasing services available"
    )
