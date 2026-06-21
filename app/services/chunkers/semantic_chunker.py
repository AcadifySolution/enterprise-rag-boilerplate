import re
import tiktoken
from typing import List, Dict, Any
from app.core.config import settings

class SemanticChunker:
    """
    Groups and splits parsed nodes into semantic, token-bounded chunks.
    """
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception:
            self.tokenizer = None

    def count_tokens(self, text: str) -> int:
        """
        Counts tokens using tiktoken (or word-split approximation as fallback).
        """
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        return len(text.split())

    def chunk_node(self, node: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Splits a hierarchical node's text into chunks respecting semantic splits and token limits.
        """
        text = node["text"]
        # Basic sentence division regex
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
        if not sentences:
            return []
            
        chunks = []
        current_chunk_sentences = []
        current_chunk_tokens = 0
        
        # Heuristic semantic transitions favoring split boundaries
        semantic_transitions = {
            "however", "therefore", "furthermore", "consequently", 
            "nevertheless", "finally", "meanwhile", "additionally", 
            "specifically", "moreover", "in contrast"
        }

        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)
            
            # Detect starting transition words
            words = sentence.split()
            first_word = words[0].lower().strip(",.?!") if words else ""
            is_transition = first_word in semantic_transitions
            
            # Conditions for splitting:
            # 1. Hard overflow limit.
            # 2. Semantic transition starting word (with reasonable current chunk length).
            if (current_chunk_tokens + sentence_tokens > self.chunk_size) or \
               (is_transition and current_chunk_tokens > (self.chunk_size // 2)):
                
                if current_chunk_sentences:
                    chunks.append(" ".join(current_chunk_sentences))
                
                # Apply overlapping logic
                overlap_sentences = []
                overlap_tokens = 0
                for s in reversed(current_chunk_sentences):
                    s_tokens = self.count_tokens(s)
                    if overlap_tokens + s_tokens <= self.chunk_overlap:
                        overlap_sentences.insert(0, s)
                        overlap_tokens += s_tokens
                    else:
                        break
                current_chunk_sentences = overlap_sentences
                current_chunk_tokens = overlap_tokens

            current_chunk_sentences.append(sentence)
            current_chunk_tokens += sentence_tokens

        if current_chunk_sentences:
            chunks.append(" ".join(current_chunk_sentences))

        # Build final chunk list
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
