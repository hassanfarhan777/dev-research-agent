"""
workflow.py

This module defines the orchestration logic for the Developer Tools Research Agent using LangGraph.
It implements a state machine that processes a developer's query through the following stages:

1. Tool Extraction → 2. Research → 3. Analysis & Recommendation

Components:
- LangGraph: Defines the flow of each step using a state machine
- LangChain (ChatOpenAI): Handles LLM interactions
- FirecrawlService: Searches and scrapes company/tool content
- DeveloperToolsPrompts: Provides consistent prompt templates
- Pydantic models: Track structured state and outputs

Main Class:
    Workflow
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from .models import ResearchState, CompanyInfo, CompanyAnalysis
from .firecrawl_ops import FirecrawlService
from .prompts import DeveloperToolsPrompts


class Workflow:
    """
    Orchestrates the developer tools research workflow using a LangGraph state machine.

    This class builds a multi-step pipeline that:
    - Extracts tool names from content using an LLM
    - Searches for relevant companies and scrapes their websites
    - Analyzes developer-facing features using structured prompts
    - Generates a final recommendation based on all tool data
    """

    def __init__(self):
        """
        Initializes the workflow with necessary components:
        - FirecrawlService for search/scraping
        - ChatOpenAI model for LLM processing
        - DeveloperToolsPrompts for consistent prompt templates
        - A compiled LangGraph workflow pipeline
        """
        self.firecrawl = FirecrawlService()
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1, max_tokens=2000)
        self.prompts = DeveloperToolsPrompts()
        self.workflow = self._build_workflow()

    def _build_workflow(self):
        """
        Constructs the state graph that defines the sequence of processing steps.

        Returns:
            StateGraph: A compiled LangGraph instance representing the workflow.
        """
        graph = StateGraph(ResearchState)
        graph.add_node("extract_tools", self._extract_tools_step)
        graph.add_node("research", self._research_step)
        graph.add_node("analyze", self._analyze_step)

        # Define transition flow between steps
        graph.set_entry_point("extract_tools")
        graph.add_edge("extract_tools", "research")
        graph.add_edge("research", "analyze")
        graph.add_edge("analyze", END)

        return graph.compile()

    def _extract_tools_step(self, state: ResearchState) -> Dict[str, Any]:
        """
        First step: Finds articles related to the query, scrapes them, and uses an LLM to extract tool names.

        Args:
            state (ResearchState): Current state including the query.

        Returns:
            Dict[str, Any]: Updated state with extracted tool names.
        """
        print(f"Finding articles about: {state.query}")

        article_query = f"{state.query} tools comparison best alternatives"
        search_results = self.firecrawl.search_companies(article_query)

        all_content = ""
        if search_results:
            for result in search_results.data:
                url = result.get("url", "")
                scraped = self.firecrawl.scrape_company_pages(url)
                if scraped:
                    all_content += scraped.markdown[:1500] + "\n\n"

        messages = [
            SystemMessage(content=self.prompts.TOOL_EXTRACTION_SYSTEM),
            HumanMessage(content=self.prompts.tool_extraction_user(state.query, all_content))
        ]

        try:
            response = self.llm.invoke(messages)
            tools_names = [
                name.strip() 
                for name in response.content.strip().split("\n")
                if name.strip()
            ]
            print(f"Extracted tools: {', '.join(tools_names[:5])}")
            return {"extracted_tools": tools_names}
        except Exception as e:
            print(f"Error extracting tools: {e}")
            return {"extracted_tools": []}

    def _analyze_company_content(self, company_name: str, content: str) -> CompanyAnalysis:
        """
        Uses structured prompting to extract developer-relevant insights from company content.

        Args:
            company_name (str): The name of the tool or platform.
            content (str): Markdown content scraped from the website.

        Returns:
            CompanyAnalysis: Structured summary of pricing, APIs, tech stack, etc.
        """
        structured_llm = self.llm.with_structured_output(CompanyAnalysis)

        messages = [
            SystemMessage(content=self.prompts.TOOL_ANALYSIS_SYSTEM),
            HumanMessage(content=self.prompts.tool_analysis_user(company_name, content))
        ]

        try:
            analysis = structured_llm.invoke(messages)
            return analysis
        except Exception as e:
            print(e)
            return CompanyAnalysis(
                pricing_model="Unknown",
                is_open_source=None,
                tech_stack=[],
                description="Failed",
                api_available=None,
                language_support=[],
                integration_capabilities=[]
            )

    def _research_step(self, state: ResearchState) -> Dict[str, Any]:
        """
        Second step: Searches for tool websites and extracts structured company info.

        Args:
            state (ResearchState): Current state with extracted tool names.

        Returns:
            Dict[str, Any]: Updated state with populated CompanyInfo objects.
        """
        extracted_tools = getattr(state, "extracted_tools", [])

        if not extracted_tools:
            print("No tools extracted, falling back to direct search.")
            search_results = self.firecrawl.search_companies(state.query)
            tools_names = [
                result.get("metadata", {}).get("title", "Unknown")
                for result in search_results.data
            ]
        else:
            tools_names = extracted_tools[:4]

        print(f"Researching {len(tools_names)} tools: {', '.join(tools_names)}")

        companies = []
        for tool_name in tools_names:
            tool_search_results = self.firecrawl.search_companies(tool_name + " official site")

            if tool_search_results and tool_search_results.data:
                result = tool_search_results.data[0]
                url = result.get("url", "")

                company = CompanyInfo(
                    name=tool_name,
                    description=result.get("markdown", ""),
                    website=url
                )

                scraped = self.firecrawl.scrape_company_pages(url)
                if scraped:
                    content = scraped.markdown
                    analysis = self._analyze_company_content(company.name, content)

                    # Populate developer-specific fields from analysis
                    company.pricing_model = analysis.pricing_model
                    company.is_open_source = analysis.is_open_source
                    company.tech_stack = analysis.tech_stack
                    company.description = analysis.description
                    company.api_available = analysis.api_available
                    company.language_support = analysis.language_support
                    company.integration_capabilities = analysis.integration_capabilities

                companies.append(company)

        return {"companies": companies}

    def _analyze_step(self, state: ResearchState) -> Dict[str, Any]:
        """
        Final step: Generates developer recommendations based on analyzed companies.

        Args:
            state (ResearchState): Current state with populated company data.

        Returns:
            Dict[str, Any]: Updated state with a final recommendation string.
        """
        print("Generating recommendations based on company data...")

        company_data = ", ".join([
            company.json() for company in state.companies
        ])

        messages = [
            SystemMessage(content=self.prompts.RECOMMENDATIONS_SYSTEM),
            HumanMessage(content=self.prompts.recommendations_user(state.query, company_data))
        ]

        response = self.llm.invoke(messages)
        return {
            "analysis": response.content
        }

    def run(self, query: str) -> ResearchState:
        """
        Public method to run the full workflow on a user-provided query.

        Args:
            query (str): Developer question or topic to research (e.g., "best observability tools").

        Returns:
            ResearchState: Final state containing extracted tools, company data, and recommendations.
        """
        initial_state = ResearchState(query=query)
        final_state = self.workflow.invoke(initial_state)
        return ResearchState(**final_state)