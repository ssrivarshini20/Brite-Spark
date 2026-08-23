import re
import os
from typing import List, Dict, Any

def parse_policy_manual(file_path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Policy manual not found at {file_path}")
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    chunks = []
    current_part = ""
    current_section = ""
    
    lines = content.split('\n')
    
    current_clause_num = ""
    current_clause_text = []
    
    def save_clause():
        if current_clause_num and current_clause_text:
            text_content = " ".join([t for t in current_clause_text if t.strip()])
            chunks.append({
                "document": "policy-manual.md",
                "section": f"{current_part} - {current_section}".strip(" -"),
                "clause": f"§{current_clause_num}",
                "source_text": f"**{current_clause_num}** {text_content}"
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
            match = re.match(r'^\*\*(\d+\.\d+\.\d+)\*\*(.*)', line_stripped)
            if match:
                save_clause()
                current_clause_num = match.group(1).strip()
                current_clause_text = [match.group(2).strip()]
            else:
                if current_clause_num:
                    current_clause_text.append(line_stripped)
                    
    save_clause()
    
    return chunks
