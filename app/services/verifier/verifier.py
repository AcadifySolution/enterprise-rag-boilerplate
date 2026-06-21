import re
from typing import List, Dict, Any

class ResponseVerifier:
    """
    Validates LLM-generated responses against retrieved source context chunks.
    Calculates groundedness scoring and traces citations using cosine similarity.
    """
    @classmethod
    def _get_bow(cls, text: str) -> Dict[str, int]:
        """
        Extracts lowercase word counts for term-frequency modeling.
        """
        words = re.findall(r'\w+', text.lower())
        vector = {}
        for w in words:
            vector[w] = vector.get(w, 0) + 1
        return vector

    @classmethod
    def _cosine_similarity(cls, vec1: Dict[str, int], vec2: Dict[str, int]) -> float:
        """
        Calculates cosine similarity between two word count dictionaries.
        """
        if not vec1 or not vec2:
            return 0.0
        intersection = set(vec1.keys()) & set(vec2.keys())
        dot_product = sum(vec1[w] * vec2[w] for w in intersection)
        
        sum1 = sum(v ** 2 for v in vec1.values())
        sum2 = sum(v ** 2 for v in vec2.values())
        denominator = (sum1 * sum2) ** 0.5
        
        if not denominator:
            return 0.0
        return dot_product / denominator

    @classmethod
    def verify(cls, response: str, contexts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculates groundedness scoring and traces citations for each claim.
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
            sentence_words = re.findall(r'\w+', sentence.lower())
            if len(sentence_words) < 3:
                # Treat very short/transitional sentences as implicitly grounded
                grounded_sentences += 1
                continue
                
            v_sentence = cls._get_bow(sentence)
            best_chunk = None
            best_score = 0.0

            # Measure overlap against retrieved context chunks using cosine similarity
            for ctx in contexts:
                v_ctx = cls._get_bow(ctx["text"])
                similarity = cls._cosine_similarity(v_sentence, v_ctx)
                if similarity > best_score:
                    best_score = similarity
                    best_chunk = ctx

            # Groundedness threshold set at 25% cosine similarity
            is_grounded = best_score >= 0.25
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
