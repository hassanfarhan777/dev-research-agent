"""
prompts.py

This module defines structured prompts for guiding a language model (LLM) to perform tasks related to developer tools research.
It includes system prompts and dynamic user prompts for:
- Extracting tool names from articles
- Analyzing tools/companies from scraped content
- Generating developer-focused recommendations

These prompts are used in conjunction with LangChain/LLM workflows to produce structured and actionable insights.
"""


class DeveloperToolsPrompts:
    """
    Collection of prompt templates for analyzing developer tools and technologies.

    This class provides reusable templates and prompt-building methods to instruct a language model
    on how to extract tool names, analyze tool characteristics, and generate recommendations.
    """

    # ---------- TOOL EXTRACTION ----------

    TOOL_EXTRACTION_SYSTEM = """You are a tech researcher. Extract specific tool, library, platform, or service names from articles.
                            Focus on actual products/tools that developers can use, not general concepts or features."""

    @staticmethod
    def tool_extraction_user(query: str, content: str) -> str:
        """
        Generate a user prompt to extract tool names from article content.

        Args:
            query (str): The original developer-related query (e.g., "frontend monitoring").
            content (str): Scraped article or website content.

        Returns:
            str: A prompt instructing the LLM to extract relevant tool names.
        """
        return f"""Query: {query}
                Article Content: {content}

                Extract a list of specific tool/service names mentioned in this content that are relevant to "{query}".

                Rules:
                - Only include actual product names, not generic terms
                - Focus on tools developers can directly use/implement
                - Include both open source and commercial options
                - Limit to the 5 most relevant tools
                - Return just the tool names, one per line, no descriptions

                Example format:
                Supabase
                PlanetScale
                Railway
                Appwrite
                Nhost"""

    # ---------- TOOL ANALYSIS ----------

    TOOL_ANALYSIS_SYSTEM = """You are analyzing developer tools and programming technologies. 
                            Focus on extracting information relevant to programmers and software developers. 
                            Pay special attention to programming languages, frameworks, APIs, SDKs, and development workflows."""

    @staticmethod
    def tool_analysis_user(company_name: str, content: str) -> str:
        """
        Generate a user prompt to analyze a company's website content from a developer's perspective.

        Args:
            company_name (str): Name of the company/tool being analyzed.
            content (str): Scraped markdown or raw text from the company's website.

        Returns:
            str: A prompt asking the LLM to extract structured developer-relevant insights.
        """
        return f"""Company/Tool: {company_name}
                Website Content: {content[:2500]}

                Analyze this content from a developer's perspective and provide:
                - pricing_model: One of "Free", "Freemium", "Paid", "Enterprise", or "Unknown"
                - is_open_source: true if open source, false if proprietary, null if unclear
                - tech_stack: List of programming languages, frameworks, databases, APIs, or technologies supported/used
                - description: Brief 1-sentence description focusing on what this tool does for developers
                - api_available: true if REST API, GraphQL, SDK, or programmatic access is mentioned
                - language_support: List of programming languages explicitly supported (e.g., Python, JavaScript, Go, etc.)
                - integration_capabilities: List of tools/platforms it integrates with (e.g., GitHub, VS Code, Docker, AWS, etc.)

                Focus on developer-relevant features like APIs, SDKs, language support, integrations, and development workflows."""

    # ---------- RECOMMENDATION GENERATION ----------

    RECOMMENDATIONS_SYSTEM = """You are a senior software engineer providing quick, concise tech recommendations. 
                            Keep responses brief and actionable - maximum 3-4 sentences total."""

    @staticmethod
    def recommendations_user(query: str, company_data: str) -> str:
        """
        Generate a user prompt to produce a concise recommendation based on analyzed company data.

        Args:
            query (str): The original developer's query or use case.
            company_data (str): JSON-serialized or summarized LLM output for multiple tools.

        Returns:
            str: A prompt asking the LLM to recommend the best tool with justification.
        """
        return f"""Developer Query: {query}
                Tools/Technologies Analyzed: {company_data}

                Provide a brief recommendation (3-4 sentences max) covering:
                - Which tool is best and why
                - Key cost/pricing consideration
                - Main technical advantage

                Be concise and direct - no long explanations needed."""