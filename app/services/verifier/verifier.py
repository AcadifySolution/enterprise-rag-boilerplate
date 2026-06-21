import re
from typing import List, Dict, Any

class ResponseVerifier:
    """
    Validates LLM-generated responses against retrieved source context chunks.
    Ensures groundedness (lack of hallucination) and maps individual claims to sources.
    """
    @classmethod
    def verify(cls, response: str, contexts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculates groundedness scoring and trace citations for each claim.
        """
        # Split response into individual claims (sentences)
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', response) if s.strip()]
        if not sentences or not contexts:
            return {
                "groundedness_score": 0.0,
                "is_hallucinated": True,
                "citations": []
            }

        citations = []
        grounded_sentences = 0

        for sentence in sentences:
            sentence_terms = set(re.findall(r'\w+', sentence.lower()))
            if len(sentence_terms) < 3:
                # Treat very short/transitional sentences as implicitly grounded
                grounded_sentences += 1
                continue
                
            best_chunk = None
            best_score = 0.0

            # Measure overlap against retrieved context chunks
            for ctx in contexts:
                ctx_terms = set(re.findall(r'\w+', ctx["text"].lower()))
                overlap = len(sentence_terms.intersection(ctx_terms))
                
                # Check ratio of sentence terms verified by this context
                ratio = overlap / len(sentence_terms)
                if ratio > best_score:
                    best_score = ratio
                    best_chunk = ctx

            # Groundedness threshold set at 30% word match overlap
            is_grounded = best_score >= 0.30
            if is_grounded:
                grounded_sentences += 1

            citations.append({
                "sentence": sentence,
                "source_chunk_id": best_chunk["id"] if best_chunk else None,
                "source_file": best_chunk["metadata"].get("source") if best_chunk else None,
                "overlap_score": round(best_score, 4),
                "is_grounded": is_grounded
            })

        groundedness_score = grounded_sentences / len(sentences)
        is_hallucinated = groundedness_score < 0.60

        return {
            "groundedness_score": round(groundedness_score, 2),
            "is_hallucinated": is_hallucinated,
            "citations": citations
        }
