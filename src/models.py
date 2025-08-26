from typing import List, Optional, Dict, Any
from pydantic import BaseModel

# Pydantic helps in data validation and structured output for LLM responses, in general it also provide better type hints and JSON serialization, so when you create an objectof a Pydantic model, it will automatically validate the data and ensure it conforms to the defined schema.

class CompanyAnalysis(BaseModel):
    """Summarize or analyze a company/tool’s key developer-related features"""
    pricing_model: str  # Free, Freemium, Paid, Enterprise, Unknown
    is_open_source: Optional[bool] = None
    tech_stack: List[str] = []
    description: str = ""
    api_available: Optional[bool] = None
    language_support: List[str] = []
    integration_capabilities: List[str] = []


class CompanyInfo(BaseModel):

    """Store all information you want about a specific company, from any source"""
    name: str
    description: str
    website: str
    pricing_model: Optional[str] = None
    is_open_source: Optional[bool] = None
    tech_stack: List[str] = []
    competitors: List[str] = []
    # Developer-specific fields
    api_available: Optional[bool] = None
    language_support: List[str] = []
    integration_capabilities: List[str] = []
    developer_experience_rating: Optional[str] = None  # Poor, Good, Excellent


class ResearchState(BaseModel):

    """Track all the data and process for a research/search workflow."""
    query: str
    extracted_tools: List[str] = []  # Tools extracted from articles
    companies: List[CompanyInfo] = []
    search_results: List[Dict[str, Any]] = []
    analysis: Optional[str] = None