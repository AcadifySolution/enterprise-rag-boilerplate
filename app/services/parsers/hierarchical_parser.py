import re
import uuid
from typing import List, Dict, Any

class HierarchicalParser:
    """
    Parses document contents into hierarchical chunks, preserving relationships.
    """
    @classmethod
    def parse_markdown(cls, text: str, source_name: str = "document") -> List[Dict[str, Any]]:
        """
        Parses Markdown text into hierarchical sections based on heading structures (# to ######).
        Returns a list of nodes, each mapped with a unique ID and its parent's ID.
        """
        lines = text.split("\n")
        nodes = []
        
        # Track active header nodes at each depth
        header_stack = [None] * 7  # Index matching heading level 1-6
        
        current_lines = []
        current_title = "Document Base"
        current_level = 0
        current_id = str(uuid.uuid4())
        
        def commit_node(lines_list, level, title, node_id):
            section_content = "\n".join(lines_list).strip()
            if not section_content:
                return
            
            # Identify closest parent heading
            parent_id = None
            for lvl in range(level - 1, 0, -1):
                if header_stack[lvl] is not None:
                    parent_id = header_stack[lvl]
                    break
            
            nodes.append({
                "id": node_id,
                "text": section_content,
                "metadata": {
                    "source": source_name,
                    "parent_id": parent_id,
                    "heading_level": level,
                    "heading_title": title
                }
            })

        for line in lines:
            match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if match:
                # Commit current accumulator before switching headers
                commit_node(current_lines, current_level, current_title, current_id)
                
                # Setup new heading context
                headings = match.group(1)
                level = len(headings)
                title = match.group(2).strip()
                
                new_id = str(uuid.uuid4())
                header_stack[level] = new_id
                
                # Clear nested state below current header level
                for lvl in range(level + 1, 7):
                    header_stack[lvl] = None
                
                current_level = level
                current_title = title
                current_id = new_id
                current_lines = [line]
            else:
                current_lines.append(line)
        
        # Commit final block
        commit_node(current_lines, current_level, current_title, current_id)
        return nodes
