from app.llm import call_llm

from leann.api import LeannSearcher

class ComplianceAgent:

    def __init__(self):

        self.searcher = LeannSearcher()

    async def broad_then_deep_query(self, query):

        # Broad search with LEANN

        broad_results = self.searcher.search(query)

        # For top results, perform deep analysis with PageIndex if the document is a PDF

        # For now, return broad_results

        return broad_results
