import re


def get_byte_length(pic_clause, comp_type=""):
    """Calculates the byte length of a COBOL field."""
    # Extract total digits/chars from PIC (e.g., S9(3)V99 -> 5)
    matches = re.findall(r'\((\+d)\)', pic_clause)

    # Handle simple X(n) or 9(n)
    total_len = 0
    clean_pic = re.sub(r'\((\d+)\)', lambda m: int(m.group(1)) * pic_clause[m.start() - 1], pic_clause)
    total_len = len(re.sub(r'[SVX9.]', '1', clean_pic).split()[0])

    if "COMP-3" in comp_type:
        # Packed Decimal: (digits + 1) / 2 rounded up
        return (total_len // 2) + 1
    elif "COMP" in comp_type:
        # Binary: Usually 2, 4, or 8 bytes based on digits
        if total_len <= 4: return 2
        if total_len <= 9: return 4
        return 8

    return total_len


def parse_cobol_to_sql(file_content):
    lines = [line.strip() for line in file_content.split('\n') if line.strip()]
    record_name = lines[0].split()[1].replace('.', '')

    fields = []
    # Simplified regex to capture Level, Name, Pic, Occurs, and Comp
    pattern = re.compile(r'^(\d+)\s+([\w-]+)(?:\s+PIC\s+([\w\(\)V]+))?(?:\s+OCCURS\s+(\d+))?(?:\s+(COMP(?:-\d)?))?')

    # We use a stack to manage levels and a list to store raw objects
    nodes = []
    for line in lines[1:]:
        match = pattern.match(line)
        if not match: continue

        lvl, name, pic, occurs, comp = match.groups()
        if lvl in ['66', '77', '88']: continue

        nodes.append({
            'lvl': int(lvl),
            'name': name,
            'pic': pic,
            'occurs': int(occurs) if occurs else 1,
            'comp': comp if comp else "",
            'children': []
        })

    # Build hierarchy
    root_children = []
    stack = []
    for node in nodes:
        while stack and stack[-1]['lvl'] >= node['lvl']:
            stack.pop()
        if not stack:
            root_children.append(node)
        else:
            stack[-1]['children'].append(node)
        stack.append(node)

    results = []
    current_pos = 1

    def process_node(node):
        nonlocal current_pos
        for _ in range(node['occurs']):
            if node['pic']:
                length = get_byte_length(node['pic'], node['comp'])
                results.append(f"SUBSTR({record_name}, {current_pos}, {length})")
                current_pos += length
            else:
                for child in node['children']:
                    process_node(child)

    for node in root_children:
        process_node(node)

    return ", ".join(results)


# Testing with Example 2
cobol_input = """01  RECNAME.
    05 FLD1             PIC X(3).
    05 FLD2             PIC X(5) OCCURS 3.
    05 FLD3             OCCURS 2.
       10 FLD3A         PIC X(2).
       10 FLD3B         PIC X(3).
    05 FLD4             PIC X(5)."""

print(parse_cobol_to_sql(cobol_input))