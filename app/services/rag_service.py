from typing import List, Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings
from app.core.pii_masking import PIIMasker
from app.services.retriever.multi_stage_retriever import MultiStageRetriever
from app.services.verifier.verifier import ResponseVerifier
from app.core.logging import logger

class RAGService:
    """
    Orchestrates the entire RAG pipeline sequence.
    """
    def __init__(self):
        self.retriever = MultiStageRetriever()
        self.llm = None
        
        # Instantiate real Anthropic Claude gateway if configurations allow
        if settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY != "your-anthropic-api-key-here":
            try:
                from langchain_anthropic import ChatAnthropic
                self.llm = ChatAnthropic(
                    anthropic_api_key=settings.ANTHROPIC_API_KEY,
                    model_name="claude-3-5-sonnet-20240620"
                )
                logger.info("Successfully connected to Anthropic Claude gateway.")
            except ImportError:
                logger.warning("langchain-anthropic SDK not installed. Using local response synthesis fallback.")

    async def answer_query(
        self,
        query: str,
        filter_dict: Optional[Dict[str, Any]] = None,
        top_k: int = 3
    ) -> Dict[str, Any]:
        """
        Executes end-to-end lookup:
        1. Sanitize user queries to prevent PII leakage.
        2. Execute multi-stage context search.
        3. Query LLM generator (or synthesizes response offline).
        4. Validate groundedness and compile claim citations.
        """
        # 1. PII query interception
        masked_query = PIIMasker.mask_text(query)
        logger.info(f"Query check complete. Processing query: {masked_query}")
        
        # 2. Retrieve contexts
        contexts = await self.retriever.retrieve(
            query=masked_query,
            top_k=top_k,
            filter_dict=filter_dict
        )
        
        if not contexts:
            return {
                "query": masked_query,
                "answer": "No relevant context documents were found to answer your query.",
                "contexts": [],
                "verification": {
                    "groundedness_score": 1.0,
                    "is_hallucinated": False,
                    "citations": []
                }
            }

        # Combine context passages
        context_str = "\n\n".join([f"[Source Chunk ID: {c['id']}]\n{c['text']}" for c in contexts])

        # 3. Model Generation
        if self.llm:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert systems assistant. Answer the user's question using ONLY the provided contexts. Cite the Source Chunk ID where appropriate.\n\nContexts:\n{context}"),
                ("human", "{question}")
            ])
            chain = prompt | self.llm
            response = await chain.ainvoke({"context": context_str, "question": masked_query})
            answer = response.content
        else:
            # Synthesize deterministic mock reply from retrieved text segments
            claims = []
            for ctx in contexts:
                lines = [l.strip() for l in ctx["text"].split("\n") if l.strip()]
                # Pull first sentence or line to represent a claim
                claim = lines[0] if lines else "Document segment content."
                claims.append(f"{claim}")
            answer = " ".join(claims)

        # 4. Groundedness validation
        verification = ResponseVerifier.verify(answer, contexts)
        
        return {
            "query": masked_query,
            "answer": answer,
            "contexts": contexts,
            "verification": verification
        }
