"""Plagiarism checking service caller."""
from typing import Any

import httpx

from backend.models import ServiceResult


async def check_plagiarism(text: str, service_config: dict[str, Any]) -> ServiceResult:
    """Check text for plagiarism using an external service.
    
    Args:
        text: Text content to check.
        service_config: Service configuration with name, api_url, api_key.
    
    Returns:
        ServiceResult with plagiarism check results.
    """
    service_name = service_config.get("name", "Unknown Service")
    api_url = service_config.get("api_url", "")
    api_key = service_config.get("api_key", "")
    
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
            
            return ServiceResult(
                service_name=service_name,
                service_type="plagiarism",
                success=True,
                result=result_data
            )
    
    except httpx.TimeoutException:
        return ServiceResult(
            service_name=service_name,
            service_type="plagiarism",
            success=False,
            error="Request timed out"
        )
    except httpx.HTTPStatusError as e:
        return ServiceResult(
            service_name=service_name,
            service_type="plagiarism",
            success=False,
            error=f"HTTP error: {e.response.status_code}"
        )
    except Exception as e:
        return ServiceResult(
            service_name=service_name,
            service_type="plagiarism",
            success=False,
            error=str(e)
        )


async def check_all_plagiarism_services(
    text: str, 
    services: list[dict[str, Any]]
) -> list[ServiceResult]:
    """Check text against all enabled plagiarism services.
    
    Args:
        text: Text content to check.
        services: List of enabled plagiarism service configurations.
    
    Returns:
        List of ServiceResult from all services.
    """
    results = []
    for service in services:
        result = await check_plagiarism(text, service)
        results.append(result)
    return results
