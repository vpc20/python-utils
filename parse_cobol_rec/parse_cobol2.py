import re


def get_field_length(pic, comp=""):
    if not pic: return 0
    # Expand PIC clauses like X(3) -> XXX
    expanded = re.sub(r'\((\d+)\)', lambda m: int(m.group(1)) * "X", pic)
    base_len = len(re.sub(r'[SV.]', '', expanded))

    if "COMP-3" in comp:
        return (base_len // 2) + 1
    if "COMP" in comp:
        return 2 if base_len <= 4 else 4 if base_len <= 9 else 8
    return base_len


def parse_cobol_file(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    # Get Record Name from Level 01
    rec_match = re.search(r'01\s+([\w-]+)', lines[0])
    rec_name = rec_match.group(1).rstrip('.') if rec_match else "RECORD"

    nodes = []
    # Regex to capture: Level, Name, Redefines, Pic, Occurs, Comp
    pattern = re.compile(
        r'(?P<lvl>\d+)\s+(?P<name>[\w-]+)'
        r'(?:\s+REDEFINES\s+(?P<ref>[\w-]+))?'
        r'(?:\s+PIC\s+(?P<pic>[\w\(\)V.]+))?'
        r'(?:\s+OCCURS\s+(?P<occ>\d+))?'
        r'(?:\s+(?P<comp>COMP(?:-\d)?))?', re.I
    )

    # 1. Build a flat list of nodes
    for line in lines[1:]:
        m = pattern.search(line.rstrip('.'))
        if not m or m.group('lvl') in ['66', '77', '88']: continue
        nodes.append({
            'lvl': int(m.group('lvl')),
            'name': m.group('name'),
            'ref': m.group('ref'),
            'pic': m.group('pic'),
            'occ': int(m.group('occ') or 1),
            'comp': m.group('comp') or "",
            'children': []
        })

    # 2. Build the Tree Structure
    root_elements = []
    stack = []
    for node in nodes:
        while stack and stack[-1]['lvl'] >= node['lvl']:
            stack.pop()
        if not stack:
            root_elements.append(node)
        else:
            stack[-1]['children'].append(node)
        stack.append(node)

    results = []
    current_pos = 1
    field_starts = {}  # Tracks starting positions for REDEFINES

    def process_node(node, start_ptr):
        local_ptr = start_ptr
        node_total_len = 0

        for _ in range(node['occ']):
            iteration_ptr = local_ptr
            if node['pic']:
                f_len = get_field_length(node['pic'], node['comp'])
                results.append(f"SUBSTR({rec_name}, {iteration_ptr}, {f_len})")
                iteration_ptr += f_len
            else:
                for child in node['children']:
                    # Handle REDEFINES within groups
                    if child['ref']:
                        child_start = field_starts.get(child['ref'], iteration_ptr)
                    else:
                        child_start = iteration_ptr

                    c_len = process_node(child, child_start)
                    # Only advance pointer if child is NOT a redefinition
                    if not child['ref']:
                        iteration_ptr += c_len

            # Store the start of this named field for future REDEFINES
            field_starts[node['name']] = local_ptr

            if _ == 0:  # Calculate length of one occurrence
                node_total_len = iteration_ptr - local_ptr
            local_ptr = iteration_ptr

        return local_ptr - start_ptr

    # 3. Generate Output
    for root in root_elements:
        if root['ref']:
            current_pos = field_starts.get(root['ref'], current_pos)

        consumed = process_node(root, current_pos)

        if not root['ref']:
            current_pos += consumed

    return ", ".join(results)


# Execution
if __name__ == "__main__":
    print(parse_cobol_file('input1.txt'))