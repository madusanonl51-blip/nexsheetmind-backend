from rapidfuzz import fuzz
from app.core.models import ColumnMapping

KNOWN_ALIASES = {
    'dob': ['date of birth', 'birth date', 'birthdate'],
    'id': ['employee id', 'emp id', 'staff id', 'worker id', 'person id'],
    'name': ['full name', 'employee name', 'staff name'],
    'salary': ['wage', 'pay', 'compensation', 'income'],
    'dept': ['department', 'division', 'unit'],
    'phone': ['mobile', 'contact', 'telephone', 'cell'],
    'email': ['email address', 'e-mail', 'mail']
}

def detect_column_mappings(columns_a: list[str], columns_b: list[str]) -> list[ColumnMapping]:
    mappings = []
    mapped_b = set()
    
    for col_a in columns_a:
        best_match = None
        best_score = 0
        best_col_b = None
        
        col_a_lower = col_a.lower()
        aliases_a = [col_a_lower]
        for key, aliases in KNOWN_ALIASES.items():
            if col_a_lower == key or col_a_lower in aliases:
                aliases_a.extend(aliases)
                if key not in aliases_a:
                    aliases_a.append(key)
                
        for col_b in columns_b:
            if col_b in mapped_b:
                continue
                
            col_b_lower = col_b.lower()
            aliases_b = [col_b_lower]
            for key, aliases in KNOWN_ALIASES.items():
                if col_b_lower == key or col_b_lower in aliases:
                    aliases_b.extend(aliases)
                    if key not in aliases_b:
                        aliases_b.append(key)
            
            if set(aliases_a) & set(aliases_b):
                score = 100.0
            else:
                score1 = fuzz.token_sort_ratio(col_a_lower, col_b_lower)
                score2 = fuzz.partial_ratio(col_a_lower, col_b_lower)
                score = max(score1, score2)
                
            if score > best_score:
                best_score = score
                best_col_b = col_b
                
        if best_score >= 60 and best_col_b is not None:
            mappings.append(ColumnMapping(
                source_column=col_a,
                target_column=best_col_b,
                confidence=best_score / 100.0,
                is_key=False
            ))
            mapped_b.add(best_col_b)
            
    return mappings
