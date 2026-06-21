import re
import tiktoken
from typing import List, Dict, Any
from app.core.config import settings

class SemanticChunker:
    """
    Partitions documents using cosine similarity thresholds between adjacent sentences.
    Provides mathematically-grounded semantic boundary detection.
    """
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None, similarity_threshold: float = 0.25):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        self.similarity_threshold = similarity_threshold
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception:
            self.tokenizer = None

    def count_tokens(self, text: str) -> int:
        """
        Counts tokens using tiktoken encoder, falling back to word length.
        """
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        return len(text.split())

    def _get_bow(self, text: str) -> Dict[str, int]:
        """
        Extracts lowercase word counts for term-frequency similarity modeling.
        """
        words = re.findall(r'\w+', text.lower())
        vector = {}
        for w in words:
            vector[w] = vector.get(w, 0) + 1
        return vector

    def _cosine_similarity(self, vec1: Dict[str, int], vec2: Dict[str, int]) -> float:
        """
        Calculates cosine similarity between bag-of-words representation vectors.
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

    def chunk_node(self, node: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Splits a single node's text by detecting thematic shifts and token overflow.
        """
        text = node["text"]
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
        if not sentences:
            return []
            
        chunks = []
        current_sentences = []
        current_tokens = 0

        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)
            
            # Identify thematic gaps using cosine similarity between adjacent sentences
            thematic_gap = False
            if current_sentences:
                prev_sentence = current_sentences[-1]
                v1 = self._get_bow(prev_sentence)
                v2 = self._get_bow(sentence)
                similarity = self._cosine_similarity(v1, v2)
                
                # If similarity is low and current chunk is large enough, trigger split
                if similarity < self.similarity_threshold and current_tokens > (self.chunk_size // 3):
                    thematic_gap = True
            
            if (current_tokens + sentence_tokens > self.chunk_size) or thematic_gap:
                if current_sentences:
                    chunks.append(" ".join(current_sentences))
                
                # Apply sliding overlap
                overlap_sentences = []
                overlap_tokens = 0
                for s in reversed(current_sentences):
                    s_tokens = self.count_tokens(s)
                    if overlap_tokens + s_tokens <= self.chunk_overlap:
                        overlap_sentences.insert(0, s)
                        overlap_tokens += s_tokens
                    else:
                        break
                current_sentences = overlap_sentences
                current_tokens = overlap_tokens

            current_sentences.append(sentence)
            current_tokens += sentence_tokens

        if current_sentences:
            chunks.append(" ".join(current_sentences))

        # Build chunks with parents and token details
        chunked_nodes = []
        for idx, chunk_text in enumerate(chunks):
            chunked_nodes.append({
                "id": f"{node['id']}_chunk_{idx}",
                "text": chunk_text,
                "metadata": {
                    **node["metadata"],
                    "parent_chunk_id": node["id"],
                    "chunk_index": idx,
                    "token_count": self.count_tokens(chunk_text)
                }
            })
        return chunked_nodes
