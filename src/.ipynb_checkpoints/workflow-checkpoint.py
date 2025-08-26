# from typing import Dict, Any
# from langgraph.graph import StateGraph, END
# from langchain_openai import ChatOpenAI
# from langchain_core.messages import HumanMessage, SystemMessage
# from .models import ResearchState, CompanyInfo, CompanyAnalysis
# from .firecrawl_ops import FirecrawlService
# from .prompts import DeveloperToolsPrompts

# class Workflow:
#     """State machine workflow for developer tools research and analysis"""

#     def __init__(self):
#         self.firecrawl = FirecrawlService()
#         self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1, max_tokens=2000)
#         self.prompts = DeveloperToolsPrompts()
#         self.workflow = self._build_workflow()


#     def _build_workflow(self) :  # the underscore indicates this is a private method

#         graph = StateGraph(ResearchState)
#         graph.add_node("extract_tools", self._extract_tools_step)
#         graph.add_node("research", self._research_step)
#         graph.add_node("analyze", self._analyze_step)
#         graph.set_entry_point("extract_tools")
#         graph.add_edge("extract_tools", "research")
#         graph.add_edge("research", "analyze")
#         graph.add_edge("analyze", END)
#         return graph.compile()
#         # It runs the state machine workflow though the stages, its the graph that defines the steps and transitions in the workflow.


#     def _extract_tools_step(self, state: ResearchState) -> Dict[str, Any]:
       
        
#         print(F" Finding articles about: {state.query}")
        
#         article_query = f"{state.query} tools comparison best alternatives"
#         search_results = self.firecrawl.search_companies(article_query, num_results=5)
#         # It looks up the URLs of articles related to the query and extracts the content from them.

        
#         all_content = ""

#         for result in search_results.data:
#             url = result.get("url", "")
#             scraped = self.firecrawl.scrape_company_pages(url)
#             if scraped:
#                 all_content += scraped.markdown[:1500] + "\n\n"
#         # Find the contents from those URLs and concatenate them into a single string.

#         messages = [
#             SystemMessage(content=self.prompts.TOOL_EXTRACTION_SYSTEM),
#             HumanMessage(content=self.prompts.tool_extraction_user(state.query, all_content))
#         ]
#         # Prepare the messages for the LLM, including a system message and a user message with the query and content.

#         try:
            
#             response = self.llm.invoke(messages)
#             tools_names = [
#                 name.strip() 
#                 for name in response.content.strip().split("\n")
#                 if name.strip()  # Ensure no empty lines
#             ] 
#             # Extract tool names from the LLM response, ensuring they are clean and non-empty.


#             print(f"Extracted tools: {', '.join(tools_names[:5])}")
#             return {"extracted_tools": tools_names}
        
#         except Exception as e:
#             print(f"Error extracting tools: {e}")
#             return {"extracted_tools": []}
        



#     # Workflow Step 2 : Analyze Company URLs

#     def _analyze_company_content( self, company_name : str, content: str) -> CompanyAnalysis: 
#         structured_llm = self.llm.with_structured_output(CompanyAnalysis) 

#         messages = [
#                 SystemMessage(content=self.prompts.COMPANY_ANALYSIS_SYSTEM),
#                 HumanMessage(content=self.prompts.tool_analysis_user(company_name, content))
#             ]
        
#         try : 
#             analysis = structured_llm.invoke(messages)
#             return analysis
        
#         except Exception as e:
#             print(e)
#             return CompanyAnalysis(
#                 pricing_model="Unknown",
#                 is_open_source=None,
#                 tech_stack=[],
#                 description="Failed",
#                 api_available=None,
#                 language_support=[],
#                 integration_capabilities=[]
#             )

#     def _research_step(self, state: ResearchState) -> Dict[str, Any]:
#         extracted_tools =  getattr(state, "extracted_tools", [])



#         if not extracted_tools:
#             print("No tools extracted, falling back to direct search.")
#             search_results = self.firecrawl.search_companies(state.query, num_results=4)

#             tools_names = [
#                 result.get("metadata", {}).get("title", "Unknown")
#                 for result in search_results.data
#             ]

#         # If no tools were extracted, it searches directly for the query and limits the results to 4 tools.

#         else:
#             tools_names = extracted_tools[:4] # Limit to first 4 tools

#         print(f"Researching {len(tools_names)} tools: {', '.join(tools_names)}")

#         companies = []
#         for tool_name in tools_names:
#             tool_search_results = self.firecrawl.search_companies(tool_name + "official site", num_results=1 )
#             # Finds URLs of the official site of the tools found from the previous step


#             if tool_search_results:
#                 result = tool_search_results.data[0]
#                 url = result.get("url", "")

#                 company = CompanyInfo(
#                     name=tool_name,
#                     description=result.get("markdown",""),
#                     website=url,
#                     tech_stack=[],
#                     competitors=[]
#                 )

#                 # This part gives the company a description and website URL


#                 scraped = self.firecrawl.scrape_company_pages(url)
#                 if scraped:
#                     content = scraped.markdown
#                     analysis = self._analyze_company_content(company.name, content)
#                     # Analyzes the content of the company page using the LLM

#                     company.pricing_model = analysis.pricing_model
#                     company.is_open_source = analysis.is_open_source
#                     company.tech_stack = analysis.tech_stack
#                     company.description = analysis.description
#                     company.api_available = analysis.api_available
#                     company.language_support = analysis.language_support
#                     company.integration_capabilities = analysis.integration_capabilities
#                     # Scrapes the company page and updates the company information with the analysis results

#                 companies.append(company)


#             return {
#                 "companies": companies
#                 }


#     def _analyze_step(self, state: ResearchState) -> Dict[str, Any]:
        
#         print("Generating recommendations based on company data...")

#         company_data = ", ".join([
#             company.json() for company in state.companies
#         ])

#         messages = [
#             SystemMessage(content=self.prompts.RECOMMENDATION_SYSTEM),
#             HumanMessage(content=self.prompts.recommendation_user(state.query, company_data))

#         ]
#         # Prepares the messages for the LLM, including a system message and a user message


#         response = self.llm.invoke(messages)
#         return {
#             "analysis": response.content
#         }
#         # Generates recommendations based on the company data using the LLM


#     def run(self, query: str) -> ResearchState:
#         """Run the workflow with the given query"""
#         initial_state = ResearchState(query=query)
#         final_state = self.workflow.invoke(initial_state)
#         return ResearchState(**final_state) # Converts the final state back to a ResearchState object
    
#         # Invokes the workflow with the initial state and returns the final state as a ResearchState. This is the main entry point for running the workflow, it takes a query and returns the final state of the research workflow.


from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .models import ResearchState, CompanyInfo, CompanyAnalysis
from .firecrawl_ops import FirecrawlService
from .prompts import DeveloperToolsPrompts

class Workflow:
    """State machine workflow for developer tools research and analysis"""

    def __init__(self):
        self.firecrawl = FirecrawlService()
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1, max_tokens=2000)
        self.prompts = DeveloperToolsPrompts()
        self.workflow = self._build_workflow()

    def _build_workflow(self) :
        graph = StateGraph(ResearchState)
        graph.add_node("extract_tools", self._extract_tools_step)
        graph.add_node("research", self._research_step)
        graph.add_node("analyze", self._analyze_step)
        graph.set_entry_point("extract_tools")
        graph.add_edge("extract_tools", "research")
        graph.add_edge("research", "analyze")
        graph.add_edge("analyze", END)
        return graph.compile()

    def _extract_tools_step(self, state: ResearchState) -> Dict[str, Any]:
        print(f"Finding articles about: {state.query}")
        
        article_query = f"{state.query} tools comparison best alternatives"
        # Removed unsupported 'num_results' parameter
        search_results = self.firecrawl.search_companies(article_query)
        
        all_content = ""
        # Added a check to ensure search_results is not None before iterating
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
        structured_llm = self.llm.with_structured_output(CompanyAnalysis) 

        messages = [
            SystemMessage(content=self.prompts.COMPANY_ANALYSIS_SYSTEM),
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
        extracted_tools = getattr(state, "extracted_tools", [])

        if not extracted_tools:
            print("No tools extracted, falling back to direct search.")
            # Removed unsupported 'num_results' parameter
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
            # Removed unsupported 'num_results' parameter
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

                    company.pricing_model = analysis.pricing_model
                    company.is_open_source = analysis.is_open_source
                    company.tech_stack = analysis.tech_stack
                    company.description = analysis.description
                    company.api_available = analysis.api_available
                    company.language_support = analysis.language_support
                    company.integration_capabilities = analysis.integration_capabilities
                
                companies.append(company)
        
        # Moved the return statement outside of the loop
        return {"companies": companies}

    def _analyze_step(self, state: ResearchState) -> Dict[str, Any]:
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
        """Run the workflow with the given query"""
        initial_state = ResearchState(query=query)
        final_state = self.workflow.invoke(initial_state)
        return ResearchState(**final_state)