import re
from typing import List, Tuple, Optional


# ---------------------------------------------------------------------------
# COMP type classification sets
# ---------------------------------------------------------------------------
PACKED_DECIMAL_TYPES = {'COMP-3', 'COMPUTATIONAL-3', 'PACKED-DECIMAL', 'COMP', 'COMPUTATIONAL'}
BINARY_TYPES         = {'COMP-4', 'COMPUTATIONAL-4', 'BINARY'}


def analyze_pic_clause(pic_clause: str) -> Tuple[int, int, bool]:
    """
    Analyse a PIC clause and return (total_digits, decimal_places, is_numeric).

    total_digits   - total number of digit positions (excluding S and V)
    decimal_places - digits after the implied decimal point (V)
    is_numeric     - True when the picture contains only 9s (and S / V), no X
    """
    if not pic_clause:
        return 0, 0, False

    pic = pic_clause.strip().upper()

    # Detect whether this is a pure numeric field (no X characters)
    is_numeric = bool(re.search(r'9', pic)) and not bool(re.search(r'X', pic))

    # ---- decimal places: count 9s after the V --------------------------------
    decimal_places = 0
    v_idx = pic.find('V')
    if v_idx != -1:
        after_v = pic[v_idx + 1:]
        for m in re.findall(r'9\((\d+)\)|9', after_v):
            decimal_places += int(m) if m else 1

    # ---- total digits: count ALL 9s and Xs (strip S first) ------------------
    clean = pic.replace('S', '').replace('V', '')
    total_digits = 0
    for m in re.findall(r'9\((\d+)\)|9', clean):
        total_digits += int(m) if m else 1
    for m in re.findall(r'X\((\d+)\)|X', clean):
        total_digits += int(m) if m else 1

    return total_digits, decimal_places, is_numeric


def binary_sql_type(total_digits: int) -> str:
    """
    Return the SQL integer type for a COMP-4 / BINARY field based on digit count.

    PIC S9(1)  to S9(4)  -> SMALLINT  (2 bytes)
    PIC S9(5)  to S9(9)  -> INTEGER   (4 bytes)
    PIC S9(10) to S9(18) -> BIGINT    (8 bytes)
    """
    if total_digits <= 4:
        return 'SMALLINT'
    elif total_digits <= 9:
        return 'INTEGER'
    else:
        return 'BIGINT'


def calculate_field_size(pic_clause: str, comp_type: Optional[str] = None) -> int:
    """
    Calculate the storage size in bytes of a COBOL field.

    Args:
        pic_clause: COBOL PICTURE clause (e.g. 'X(3)', 'S9(3)V99')
        comp_type:  Computational type keyword, or None for display fields.

    Returns:
        Size in bytes.
    """
    if not pic_clause:
        return 0

    total_digits, _, _ = analyze_pic_clause(pic_clause)

    if comp_type:
        ct = comp_type.strip().upper()
        if ct in PACKED_DECIMAL_TYPES:
            return (total_digits + 1) // 2
        if ct in BINARY_TYPES:
            if total_digits <= 4:
                return 2
            elif total_digits <= 9:
                return 4
            else:
                return 8

    return total_digits


def format_field_expr(record_name: str, position: int, size: int,
                      pic_clause: str, comp_type: Optional[str],
                      alias: str) -> str:
    """
    Build the correct SQL expression for one elementary field.

    Rules:
      Packed decimal (COMP-3 / COMPUTATIONAL-3 / PACKED-DECIMAL / COMP / COMPUTATIONAL)
          -> INTERPRET(BINARY(SUBSTR(rec, pos, size)) AS DECIMAL(total, dec)) AS alias

      Binary integer (COMP-4 / COMPUTATIONAL-4 / BINARY)
          -> INTERPRET(BINARY(SUBSTR(rec, pos, size)) AS SMALLINT|INTEGER|BIGINT) AS alias

      Zoned decimal (any display numeric field — pure 9s, with or without V)
          -> INTERPRET(BINARY(SUBSTR(rec, pos, size)) AS NUMERIC(total, dec)) AS alias

      Everything else (alphanumeric X fields)
          -> SUBSTR(rec, pos, size) AS alias
    """
    total_digits, decimal_places, is_numeric = analyze_pic_clause(pic_clause)
    substr = f"SUBSTR({record_name}, {position}, {size})"
    ct = comp_type.strip().upper() if comp_type else None
    alias = alias.replace('-', '_')

    if ct in PACKED_DECIMAL_TYPES:
        return (
            f"INTERPRET(BINARY({substr}) AS DECIMAL({total_digits}, {decimal_places}))"
            f" AS {alias}"
        )

    if ct in BINARY_TYPES:
        int_type = binary_sql_type(total_digits)
        return (
            f"INTERPRET(BINARY({substr}) AS {int_type})"
            f" AS {alias}"
        )

    if is_numeric:
        # Zoned (display) numeric — all-9 fields with no binary COMP type
        return (
            f"INTERPRET(BINARY({substr}) AS NUMERIC({total_digits}, {decimal_places}))"
            f" AS {alias}"
        )

    # Plain alphanumeric
    return f"{substr} AS {alias}"


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def parse_cobol_record(file_content: str) -> List[str]:
    """
    Parse a COBOL record definition and generate SQL expressions.

    Returns:
        List of expression strings (one per elementary field occurrence).
    """
    lines = file_content.strip().split('\n')

    # Find record name from the 01 level
    record_name = None
    for line in lines:
        m = re.match(r'\s*01\s+([\w-]+)', line)
        if m:
            record_name = m.group(1).replace('-', '_')
            break
    if not record_name:
        raise ValueError("No 01-level record found")

    # ---- collect field metadata -----------------------------------------------
    fields = []
    for line in lines:
        lm = re.match(r'\s*(\d+)\s+', line)
        if not lm:
            continue
        level = int(lm.group(1))
        if level == 1 or level in (66, 77, 88):
            continue

        parts = line.split()
        if len(parts) < 2:
            continue

        level      = int(parts[0])
        field_name = parts[1]
        pic_clause = None
        comp_type  = None
        occurs     = 1

        # PIC clause
        if 'PIC' in line.upper():
            pic_idx = next((i for i, p in enumerate(parts) if p.upper() == 'PIC'), None)
            if pic_idx is not None and pic_idx + 1 < len(parts):
                pic_clause = parts[pic_idx + 1].rstrip('.')

        # COMP / storage type
        all_comp_aliases = PACKED_DECIMAL_TYPES | BINARY_TYPES
        for part in parts:
            if part.rstrip('.').upper() in all_comp_aliases:
                comp_type = part.rstrip('.')
                break

        # OCCURS
        if 'OCCURS' in line.upper():
            oi = next((i for i, p in enumerate(parts) if p.upper() == 'OCCURS'), None)
            if oi is not None and oi + 1 < len(parts):
                occurs = int(parts[oi + 1].rstrip('.'))

        fields.append({
            'level':  level,
            'name':   field_name,
            'pic':    pic_clause,
            'comp':   comp_type,
            'occurs': occurs,
        })

    # ---- walk fields and emit expressions ------------------------------------
    expr_list = []
    position  = 1
    i         = 0

    while i < len(fields):
        field = fields[i]

        if not field['pic']:
            # Group item — expand children
            group_occurs = field['occurs']
            group_level  = field['level']

            children = []
            j = i + 1
            while j < len(fields) and fields[j]['level'] > group_level:
                children.append(fields[j])
                j += 1

            for occur_idx in range(group_occurs):
                for child in children:
                    if child['pic']:
                        size = calculate_field_size(child['pic'], child['comp'])
                        for child_occur in range(child['occurs']):
                            alias = child['name']
                            if group_occurs > 1:
                                alias += f"_{occur_idx + 1}"
                            if child['occurs'] > 1:
                                alias += f"_{child_occur + 1}"
                            expr_list.append(
                                format_field_expr(
                                    record_name, position, size,
                                    child['pic'], child['comp'], alias
                                )
                            )
                            position += size

            i = j
        else:
            # Elementary item
            size = calculate_field_size(field['pic'], field['comp'])
            for occur_idx in range(field['occurs']):
                alias = field['name']
                if field['occurs'] > 1:
                    alias += f"_{occur_idx + 1}"
                expr_list.append(
                    format_field_expr(
                        record_name, position, size,
                        field['pic'], field['comp'], alias
                    )
                )
                position += size
            i += 1

    return expr_list


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def generate_substr_from_file(filename: str) -> str:
    """Read a COBOL record definition from *filename* and return SQL expressions."""
    with open(filename, 'r') as f:
        content = f.read()
    return ',\n'.join(parse_cobol_record(content))


def generate_substr_from_text(text: str) -> str:
    """Generate SQL expressions from a COBOL record definition string."""
    return ',\n'.join(parse_cobol_record(text))


# ---------------------------------------------------------------------------
# Command-line entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python cobol_substr.py <input_file>")
        print("\nExample:")
        print("  python cobol_substr.py input1.txt")
        sys.exit(1)

    try:
        print(generate_substr_from_file(sys.argv[1]))
    except FileNotFoundError:
        print(f"Error: File '{sys.argv[1]}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)