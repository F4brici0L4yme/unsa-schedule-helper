import re

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def parse_schedule_cell(cell_val):
    if not cell_val:
        return []
        
    cell_val = re.sub(r'[-–—]\s*\n\s*([A-Z0-9])\b', r' - \1', cell_val)
    
    lines = cell_val.split('\n')
    entries = []
    current_tokens = []
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
            
        match = re.search(r'[-–—]\s*([A-Z0-9]+)$', line_clean)
        print(f"Line: {repr(line_clean)}, Match: {match}")
        if match:
            group = match.group(1)
            dash_idx = line_clean.rfind(match.group(0))
            line_left = line_clean[:dash_idx].strip()
            
            course_text = clean_text(" ".join(current_tokens + [line_left]))
            entries.append((course_text, group))
            current_tokens = []
        else:
            current_tokens.append(line_clean)
            
    if current_tokens:
        full_val = clean_text(" ".join(current_tokens))
        words = full_val.split()
        if len(words) >= 2 and len(words[-1]) == 1 and words[-1].isalnum():
            entries.append((" ".join(words[:-1]), words[-1]))
        else:
            entries.append((full_val, "UNKNOWN"))
            
    return entries

test_str = 'NEGOCIOS\nELECTRONICOS\n(E) - B\nGESTION DE\nPROYECTOS\nDE SOFTWARE - B\nAUDITORIA\nDE SISTEMAS - C'
print(parse_schedule_cell(test_str))
