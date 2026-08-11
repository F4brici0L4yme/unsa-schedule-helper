import pdfplumber
import os

def trace_unknown_rooms(filepath):
    print(f"=== Tracing UNKNOWN rooms in {filepath} ===")
    with pdfplumber.open(filepath) as pdf:
        for p_idx, page in enumerate(pdf.pages):
            tables = page.find_tables()
            for t_idx, t_obj in enumerate(tables):
                table_data = t_obj.extract()
                if not table_data or len(table_data) < 2:
                    continue
                first_row = [str(c).replace('\n', ' ').strip().upper() if c else "" for c in table_data[0]]
                
                # Check matching days
                matching_days = sum(1 for col in first_row if col in ["LUNES", "MARTES", "MIERCOLES", "MIÉRCOLES", "JUEVES", "VIERNES"])
                if matching_days < 3:
                    continue
                    
                # extract room
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
                
                table_top = t_obj.bbox[1]
                room_lines = []
                for top, line_words in lines.items():
                    if top < table_top:
                        sorted_words = sorted(line_words, key=lambda x: x['x0'])
                        line_str = " ".join([w['text'] for w in sorted_words]).strip()
                        if any(kwd in line_str.upper() for kwd in ["LABORATORIO", "AULA", "TEORIA", "TEORÍA", "AÑO"]):
                            if any(hdr in line_str.upper() for hdr in ["SIGLA", "ASIGNATURA", "ASIGNATRUA", "HORA LUNES", "GRUPO"]):
                                continue
                            room_lines.append((top, line_str))
                
                room = "UNKNOWN"
                if room_lines:
                    room_lines.sort(key=lambda x: x[0], reverse=True)
                    room = room_lines[0][1]
                    
                print(f"  Page {p_idx+1}, Table {t_idx+1}: room='{room}', bbox={t_obj.bbox}")

trace_unknown_rooms("pdf/laboratorios-2026b.pdf")
trace_unknown_rooms("pdf/teoria-2026b.pdf")
