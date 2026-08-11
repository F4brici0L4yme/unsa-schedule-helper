import pdfplumber
import csv
import re
import os

DAY_MAP = {
    "LUNES": "Lunes",
    "MARTES": "Martes",
    "MIERCOLES": "Miércoles",
    "MIÉRCOLES": "Miércoles",
    "JUEVES": "Jueves",
    "VIERNES": "Viernes"
}

SIGLA_NORMALIZATION = {
    "AFEV": "AFVE",
    "DSPJ": "DSJ",
    "IDWEB": "IDW",
    "RYCD": "RyCD",
    "RCD": "RyCD",
    "TI": "TI",
    "TRABAJO DE INVESTIGACION": "TI",
    "POLITICAS PUBLICAS Y ANTICORRUPCION": "PPA",
    "SISTEMAS OPERATIVO": "SO",
    "SISTEMAS OPERATIVOS": "SO",
    "DOO": "DSOO",
    "DESARROLLO DE SOFTWARE ORIENTADO A OBJETOS": "DSOO",
    "CAS": "CS",
}

COURSE_NAME_NORMALIZATION = {
    "AFEV": "ASPECTOS FORMALES DE VERIFICACION Y ESPECIFICACION",
    "AFVE": "ASPECTOS FORMALES DE VERIFICACION Y ESPECIFICACION",
    "ASPECTOS FORMALES DE ESPECIFICACION Y VERIFICACION": "ASPECTOS FORMALES DE VERIFICACION Y ESPECIFICACION",
    "ASPECTOS FORMALES DE VERIFICACIÓN Y ESPECIFICACIÓN": "ASPECTOS FORMALES DE VERIFICACION Y ESPECIFICACION",
    
    "TI": "TRABAJO DE INVESTIGACION",
    "TRABAJO DE INVESTIGACION": "TRABAJO DE INVESTIGACION",
    "TRABAJO DE INVESTIGACIÓN": "TRABAJO DE INVESTIGACION",
    
    "PPA": "POLITICAS PUBLICAS Y ANTICORRUPCION",
    "POLITICAS PUBLICAS Y ANTICORRUPCION": "POLITICAS PUBLICAS Y ANTICORRUPCION",
    "POLITICAS PUBLICAS Y ANTICORRUPCION (E)": "POLITICAS PUBLICAS Y ANTICORRUPCION",
    
    "SO": "SISTEMAS OPERATIVOS",
    "SISTEMAS OPERATIVO": "SISTEMAS OPERATIVOS",
    "SISTEMAS OPERATIVOS": "SISTEMAS OPERATIVOS",
    
    "DOO": "DESARROLLO DE SOFTWARE ORIENTADO A OBJETOS",
    "DSOO": "DESARROLLO DE SOFTWARE ORIENTADO A OBJETOS",
    
    "IDW": "INTRODUCCION AL DESARROLLO WEB",
    "IDWEB": "INTRODUCCION AL DESARROLLO WEB",
    "INTRODUCCIÓN AL DESARROLLO WEB": "INTRODUCCION AL DESARROLLO WEB",
    "INTRODUCCION AL DESARROLLO WEB": "INTRODUCCION AL DESARROLLO WEB",
    
    "RYCD": "REDES Y COMUNICACION DE DATOS",
    "RCD": "REDES Y COMUNICACION DE DATOS",
    "REDES Y COMUNICACION DE DATOS": "REDES Y COMUNICACION DE DATOS",
    
    "DSJ": "DESARROLLO DE SOFTWARE PARA JUEGOS",
    "DSPJ": "DESARROLLO DE SOFTWARE PARA JUEGOS",
    "DESARROLLO DE SOFTWARE PARA JUEGOS (E)": "DESARROLLO DE SOFTWARE PARA JUEGOS",
    
    "TND": "TALLER DE NARRATIVA DIGITAL",
    "TALLER DE NARRATIVA DIGITAL": "TALLER DE NARRATIVA DIGITAL",
    
    "MN": "METODOS NUMERICOS",
    
    "CALIDAD DE SOFTWARE": "CALIDAD DE SOFTWARE",
    "CONSTRUCCION DE SOFTWARE": "CONSTRUCCION DE SOFTWARE",
    "CONSTRUCCIÓN DE SOFTWARE": "CONSTRUCCION DE SOFTWARE",
}

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def normalize_sigla_and_name(sigla, name):
    sig_upper = clean_text(sigla).upper()
    name_upper = clean_text(name).upper()
    
    norm_sigla = SIGLA_NORMALIZATION.get(sig_upper, sig_upper)
    norm_name = COURSE_NAME_NORMALIZATION.get(name_upper, name_upper)
    norm_name = COURSE_NAME_NORMALIZATION.get(norm_sigla, norm_name)
    
    norm_name = re.sub(r'\s*-\s*[A-Z0-9]$', '', norm_name)
    norm_name = re.sub(r'\s*\(E\)$', '', norm_name)
    
    return norm_sigla, norm_name

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

def extract_room_name_fallback(page, table_bbox):
    words = page.extract_words()
    lines = {}
    for w in words:
        top = round(w['top'], 1)
        found = False
        for t in lines:
            if abs(t - top) < 3:
                lines[t].append(w)
                found = True
                break
        if not found:
            lines[top] = [w]
            
    table_top = table_bbox[1]
    room_lines = []
    
    for top, line_words in lines.items():
        if top < table_top:
            sorted_words = sorted(line_words, key=lambda x: x['x0'])
            line_str = " ".join([w['text'] for w in sorted_words]).strip()
            if any(kwd in line_str.upper() for kwd in ["LABORATORIO", "AULA", "TEORIA", "TEORÍA", "AÑO"]):
                if any(hdr in line_str.upper() for hdr in ["SIGLA", "ASIGNATURA", "ASIGNATRUA", "HORA LUNES", "GRUPO"]):
                    continue
                room_lines.append((top, line_str))
                
    if room_lines:
        room_lines.sort(key=lambda x: x[0], reverse=True)
        return room_lines[0][1]
    return "UNKNOWN"

def parse_pdf_file(filepath, is_lab_file, sigla_to_name, name_to_sigla):
    schedule_entries = []
    
    with pdfplumber.open(filepath) as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = page.find_tables()
            if not tables:
                continue
                
            print(f"Parsing {os.path.basename(filepath)} - Page {page_num + 1}...")
            
            # Step 1: Parse Lookup Tables
            # We keep track of lookup tables with their Y coordinate, rooms, and course-room map
            lookups = []
            
            for t_obj in tables:
                table_data = t_obj.extract()
                if not table_data or len(table_data) < 2:
                    continue
                
                first_row = [clean_text(c).upper() if c else "" for c in table_data[0]]
                matching_days = sum(1 for col in first_row if col in DAY_MAP)
                if matching_days >= 3:
                    continue # This is a schedule table
                
                header = [clean_text(c).upper() for c in table_data[0] if c is not None]
                is_lookup = False
                sigla_idx, name_idx = -1, -1
                
                # Check headers
                if "CURSO" in header and len(table_data[0]) >= 2:
                    is_lookup = True
                    sigla_idx = 0
                    name_idx = 1
                elif any("SIGLA" in h or "SIGLAS" in h for h in header):
                    is_lookup = True
                    for i, h in enumerate(table_data[0]):
                        if h and any(k in clean_text(h).upper() for k in ["SIGLA", "SIGLAS"]):
                            sigla_idx = i
                        elif h and any(k in clean_text(h).upper() for k in ["ASIGNATURA", "ASIGNATRUA"]):
                            name_idx = i
                            
                if is_lookup and sigla_idx != -1 and name_idx != -1:
                    # Find room columns in lookup table header
                    room_cols = {} # col_idx -> room_name
                    for idx, h in enumerate(table_data[0]):
                        if h and idx not in (sigla_idx, name_idx):
                            h_clean = clean_text(h).upper()
                            # Check if header contains AULA or LABORATORIO
                            room_match = re.search(r'(AULA\s+\d+|LABORATORIO\s+\d+)', h_clean)
                            if room_match:
                                room_cols[idx] = room_match.group(1)
                                
                    course_room_map = {}
                    rooms_list = list(room_cols.values())
                    
                    for row in table_data[1:]:
                        if len(row) > max(sigla_idx, name_idx):
                            sigla = clean_text(row[sigla_idx])
                            name = clean_text(row[name_idx])
                            if sigla and name:
                                sigla_norm, name_norm = normalize_sigla_and_name(sigla, name)
                                sigla_to_name[sigla_norm.upper()] = name_norm
                                name_to_sigla[name_norm.upper()] = sigla_norm.upper()
                                
                                # Check which room this course is scheduled in
                                for col_idx, r_name in room_cols.items():
                                    if col_idx < len(row) and row[col_idx] and clean_text(row[col_idx]) != "":
                                        course_room_map[sigla_norm.upper()] = r_name
                                        course_room_map[name_norm.upper()] = r_name
                                        
                    y_center = (t_obj.bbox[1] + t_obj.bbox[3]) / 2
                    lookups.append({
                        "y_center": y_center,
                        "rooms": rooms_list,
                        "course_room_map": course_room_map
                    })

            # Step 2: Parse Schedule Tables
            for t_obj in tables:
                table_data = t_obj.extract()
                if not table_data or len(table_data) < 2:
                    continue
                
                first_row = [clean_text(c).upper() if c else "" for c in table_data[0]]
                matching_days = sum(1 for col in first_row if col in DAY_MAP)
                if matching_days < 3:
                    continue
                    
                if "HORA" not in first_row:
                    continue
                    
                # Find closest lookup table on same page
                s_y_center = (t_obj.bbox[1] + t_obj.bbox[3]) / 2
                closest_lookup = None
                min_dist = float('inf')
                for l in lookups:
                    dist = abs(l["y_center"] - s_y_center)
                    if dist < min_dist:
                        min_dist = dist
                        closest_lookup = l
                        
                # Extract rooms
                rooms_from_lookup = closest_lookup["rooms"] if closest_lookup else []
                course_room_map = closest_lookup["course_room_map"] if closest_lookup else {}
                
                # Room fallback name
                fallback_room = "UNKNOWN"
                if rooms_from_lookup:
                    fallback_room = rooms_from_lookup[0]
                else:
                    room_raw = extract_room_name_fallback(page, t_obj.bbox)
                    room_clean = clean_text(room_raw)
                    room_match = re.search(r'(AULA\s+\d+|LABORATORIO\s+\d+)', room_clean, flags=re.IGNORECASE)
                    if room_match:
                        fallback_room = room_match.group(1).upper()
                
                hora_col = -1
                day_cols = {}
                for idx, col_name in enumerate(table_data[0]):
                    if not col_name:
                        continue
                    col_clean = clean_text(col_name).upper()
                    if "HORA" in col_clean:
                        hora_col = idx
                    elif col_clean in DAY_MAP:
                        day_cols[idx] = DAY_MAP[col_clean]
                        
                if hora_col == -1 or not day_cols:
                    continue
                    
                num_cols = len(table_data[0])
                last_seen_val = ["" for _ in range(num_cols)]
                # Keep track of how many consecutive times we forward filled a value
                fill_count = [0 for _ in range(num_cols)]
                
                for row_idx in range(1, len(table_data)):
                    row = table_data[row_idx]
                    time_slot = clean_text(row[hora_col])
                    if not time_slot:
                        continue
                        
                    time_match = re.search(r'(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})', time_slot)
                    if time_match:
                        hora_inicio = time_match.group(1)
                        hora_fin = time_match.group(2)
                    else:
                        hora_inicio = time_slot
                        hora_fin = ""
                        
                    for col_idx, day_name in day_cols.items():
                        cell_val = row[col_idx]
                        
                        if cell_val is None:
                            # Forward fill up to 1 row (meaning 2 rows total, i.e. 2 periods)
                            if last_seen_val[col_idx] and fill_count[col_idx] < 1:
                                cell_val = last_seen_val[col_idx]
                                fill_count[col_idx] += 1
                            else:
                                cell_val = ""
                        else:
                            cell_val = cell_val.strip()
                            last_seen_val[col_idx] = cell_val
                            fill_count[col_idx] = 0
                            
                        if not cell_val:
                            continue
                            
                        parsed_courses = parse_schedule_cell(cell_val)
                        
                        for course_part, group in parsed_courses:
                            # Resolve room for this course
                            course_sig = course_part.upper()
                            room = course_room_map.get(course_sig, fallback_room)
                            
                            schedule_entries.append({
                                "tipo": "Laboratorio" if is_lab_file else "Teoría",
                                "ambiente": room,
                                "dia": day_name,
                                "hora_inicio": hora_inicio,
                                "hora_fin": hora_fin,
                                "curso_raw": course_part,
                                "grupo": group
                            })
                            
    return schedule_entries

def main():
    os.makedirs("export/data", exist_ok=True)
    
    sigla_to_name = {}
    name_to_sigla = {}
    
    print("Parsing PDFs...")
    lab_entries = parse_pdf_file("pdf/teoria-2026b.pdf", is_lab_file=True, sigla_to_name=sigla_to_name, name_to_sigla=name_to_sigla)
    theory_entries = parse_pdf_file("pdf/laboratorios-2026b.pdf", is_lab_file=False, sigla_to_name=sigla_to_name, name_to_sigla=name_to_sigla)
    
    all_entries = lab_entries + theory_entries
    
    resolved_records = []
    for entry in all_entries:
        raw_text = entry["curso_raw"]
        
        # Clean/normalize raw_text first to strip group noise or (E) suffixes
        _, clean_name = normalize_sigla_and_name("", raw_text)
        
        if len(raw_text) <= 6:
            # It's a sigla
            sigla = raw_text.upper()
            sigla = SIGLA_NORMALIZATION.get(sigla, sigla)
            name = sigla_to_name.get(sigla, raw_text)
            _, name = normalize_sigla_and_name("", name)
        else:
            # It's a name
            name = clean_name
            sigla = name_to_sigla.get(name.upper(), raw_text)
            sigla = SIGLA_NORMALIZATION.get(sigla.upper(), sigla)
            
        sigla, name = normalize_sigla_and_name(sigla, name)
        
        # If the resolved room name has multiple parts, split it
        # E.g. AULA 205 and AULA 301, but the map should have resolved the exact one
        resolved_records.append({
            "tipo": entry["tipo"],
            "ambiente": entry["ambiente"],
            "dia": entry["dia"],
            "hora_inicio": entry["hora_inicio"],
            "hora_fin": entry["hora_fin"],
            "curso_sigla": sigla,
            "curso_nombre": name,
            "grupo": entry["grupo"]
        })

    output_csv = "export/data/cleaned_schedule.csv"
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["tipo", "ambiente", "dia", "hora_inicio", "hora_fin", "curso_sigla", "curso_nombre", "grupo"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(resolved_records)
        
    print(f"Successfully wrote {len(resolved_records)} schedule records to {output_csv}!")

if __name__ == "__main__":
    main()
