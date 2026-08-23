import re
import os
from datetime import datetime
from typing import List, Dict, Any

def parse_policy_manual(file_path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy manual not found at {file_path}")
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    chunks = []
    document_name = os.path.basename(file_path)
    effective_match = re.search(r'\*\*Effective:\*\*\s*(\d{1,2} \w+ \d{4})', content)
    effective_from = None
    if effective_match:
        effective_from = datetime.strptime(effective_match.group(1), "%d %B %Y").date().isoformat()
    is_amendment = effective_from is not None
    current_part = ""
    current_section = ""
    
    lines = content.split('\n')
    
    current_clause_num = ""
    current_clause_text = []
    
    def save_clause():
        if current_clause_num and current_clause_text:
            text_content = " ".join([t for t in current_clause_text if t.strip()])
            chunks.append({
                "document": document_name,
                "section": f"{current_part} - {current_section}".strip(" -"),
                "clause": f"§{current_clause_num}",
                "source_text": f"**{current_clause_num}** {text_content}",
                "effective_from": effective_from,
                "is_amendment": is_amendment
            })
            
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
            
        if line_stripped.startswith("# Part "):
            save_clause()
            current_clause_num = ""
            current_clause_text = []
            current_part = line_stripped.lstrip("# ").strip()
            current_section = ""
        elif line_stripped.startswith("## "):
            save_clause()
            current_clause_num = ""
            current_clause_text = []
            current_section = line_stripped.lstrip("## ").strip()
        else:
            match = re.match(r'^\*\*(\d+(?:\.\d+)+(?:[A-Z])?)\*\*(.*)', line_stripped)
            if match:
                save_clause()
                current_clause_num = match.group(1).strip()
                current_clause_text = [match.group(2).strip()]
            else:
                if current_clause_num:
                    current_clause_text.append(line_stripped)
                    
    save_clause()
    
    return chunks
