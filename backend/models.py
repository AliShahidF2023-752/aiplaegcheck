"""Pydantic models for API requests and responses."""
from typing import Any

from pydantic import BaseModel, Field


class CheckRequest(BaseModel):
    """Request model for the /check endpoint."""
    text: str = Field(..., min_length=1, description="Text content to check")


class ServiceResult(BaseModel):
    """Result from a single external service."""
    service_name: str = Field(..., description="Name of the service")
    service_type: str = Field(..., description="Type of service (plagiarism, ai_detection, rephrasing)")
    success: bool = Field(..., description="Whether the service call was successful")
    result: dict[str, Any] = Field(default_factory=dict, description="Result data from the service")
    error: str | None = Field(None, description="Error message if the service call failed")


class CheckResponse(BaseModel):
    """Response model for the /check endpoint."""
    summary: str = Field(..., description="Human-friendly summary of all results")
    plagiarism_results: list[ServiceResult] = Field(default_factory=list, description="Results from plagiarism checkers")
    ai_detection_results: list[ServiceResult] = Field(default_factory=list, description="Results from AI detectors")
    original_text: str = Field(..., description="The original text that was checked")


class RephraseRequest(BaseModel):
    """Request model for the /rephrase endpoint."""
    text: str = Field(..., min_length=1, description="Text content to rephrase")


class RephraseResponse(BaseModel):
    """Response model for the /rephrase endpoint."""
    summary: str = Field(..., description="Human-friendly summary of results for rephrased text")
    rephrased_text: str = Field(..., description="The rephrased version of the text")
    plagiarism_results: list[ServiceResult] = Field(default_factory=list, description="Results from plagiarism checkers")
    ai_detection_results: list[ServiceResult] = Field(default_factory=list, description="Results from AI detectors")
    original_text: str = Field(..., description="The original text before rephrasing")
