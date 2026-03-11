import re
from typing import List


def calculate_field_size(pic_clause: str, comp_type: str = None) -> int:
    """
    Calculate the storage size of a COBOL field based on PIC clause and COMP type.

    Args:
        pic_clause: COBOL PICTURE clause (e.g., 'X(3)', 'S9(3)V99')
        comp_type: Computational type (COMP, COMP-3, COMP-4, BINARY, PACKED-DECIMAL, etc.)

    Returns:
        Size in bytes
    """
    if not pic_clause:
        return 0

    # Remove spaces and convert to uppercase
    pic_clause = pic_clause.strip().upper()

    # Remove S (sign) - it doesn't add to byte count in display format
    pic_clause = pic_clause.replace('S', '')

    # Remove V (decimal point indicator) - it doesn't add to storage
    pic_clause = pic_clause.replace('V', '')

    # Count total positions (digits/characters)
    total_digits = 0

    # Extract all digit counts: 9(n) or 9
    nines = re.findall(r'9\((\d+)\)|9', pic_clause)
    for nine in nines:
        if nine:  # Has parentheses
            total_digits += int(nine)
        else:  # Single 9
            total_digits += 1

    # Extract all character counts: X(n) or X
    exes = re.findall(r'X\((\d+)\)|X', pic_clause)
    for ex in exes:
        if ex:  # Has parentheses
            total_digits += int(ex)
        else:  # Single X
            total_digits += 1

    # Adjust for COMP types
    if comp_type:
        comp_type = comp_type.strip().upper()

        # Packed decimal aliases: COMP-3, COMPUTATIONAL-3, PACKED-DECIMAL, COMP, COMPUTATIONAL
        packed_decimal_types = {'COMP-3', 'COMPUTATIONAL-3', 'PACKED-DECIMAL', 'COMP', 'COMPUTATIONAL'}
        # Binary aliases: COMP-4, COMPUTATIONAL-4, BINARY
        binary_types = {'COMP-4', 'COMPUTATIONAL-4', 'BINARY'}

        if comp_type in packed_decimal_types:
            # COMP-3: packed decimal - (digits + 1) / 2
            return (total_digits + 1) // 2
        elif comp_type in binary_types:
            # COMP/BINARY: based on digit count
            if total_digits <= 4:
                return 2
            elif total_digits <= 9:
                return 4
            else:
                return 8

    return total_digits


def parse_cobol_record(file_content: str) -> List[str]:
    """
    Parse COBOL record definition and generate SQL SUBSTR functions.

    Args:
        file_content: Text content of COBOL record definition

    Returns:
        List of SUBSTR function strings with aliases
    """
    lines = file_content.strip().split('\n')

    # Find record name (01 level)
    record_name = None
    for line in lines:
        match = re.match(r'\s*01\s+(\w+)', line)
        if match:
            record_name = match.group(1)
            break

    if not record_name:
        raise ValueError("No 01 level record found")

    # Parse all fields
    fields = []
    for line in lines:
        # Skip 01 level, and levels 66, 77, 88
        level_match = re.match(r'\s*(\d+)\s+', line)
        if not level_match:
            continue

        level = int(level_match.group(1))
        if level == 1 or level in [66, 77, 88]:
            continue

        # Extract field information
        parts = line.split()
        if len(parts) < 2:
            continue

        level = int(parts[0])
        field_name = parts[1]

        # Find PIC clause
        pic_clause = None
        comp_type = None
        occurs = 1

        if 'PIC' in line.upper():
            pic_idx = next((i for i, p in enumerate(parts) if p.upper() == 'PIC'), None)
            if pic_idx is not None and pic_idx + 1 < len(parts):
                pic_clause = parts[pic_idx + 1].rstrip('.')

        # Find COMP type — match all known aliases
        comp_aliases = {
            'COMP', 'COMPUTATIONAL',
            'COMP-3', 'COMPUTATIONAL-3', 'PACKED-DECIMAL',
            'COMP-4', 'COMPUTATIONAL-4', 'BINARY'
        }
        for part in parts:
            if part.rstrip('.').upper() in comp_aliases:
                comp_type = part.rstrip('.')
                break

        # Find OCCURS
        if 'OCCURS' in line.upper():
            occurs_idx = next((i for i, p in enumerate(parts) if p.upper() == 'OCCURS'), None)
            if occurs_idx is not None and occurs_idx + 1 < len(parts):
                occurs = int(parts[occurs_idx + 1].rstrip('.'))

        fields.append({
            'level': level,
            'name': field_name,
            'pic': pic_clause,
            'comp': comp_type,
            'occurs': occurs
        })

    # Generate SUBSTR functions
    substr_list = []
    position = 1

    i = 0
    while i < len(fields):
        field = fields[i]

        # Check if this is a group item (no PIC clause)
        if not field['pic']:
            # Group item - process children
            group_occurs = field['occurs']
            group_level = field['level']

            # Find all children of this group
            children = []
            j = i + 1
            while j < len(fields) and fields[j]['level'] > group_level:
                children.append(fields[j])
                j += 1

            # Process group OCCURS times
            for occur_idx in range(group_occurs):
                for child in children:
                    if child['pic']:  # Only elementary items
                        size = calculate_field_size(child['pic'], child['comp'])
                        for child_occur in range(child['occurs']):
                            # Build alias: append occurrence suffixes when needed
                            alias = child['name']
                            if group_occurs > 1:
                                alias += f"_{occur_idx + 1}"
                            if child['occurs'] > 1:
                                alias += f"_{child_occur + 1}"
                            substr_list.append(
                                f"SUBSTR({record_name}, {position}, {size}) AS {alias}"
                            )
                            position += size

            i = j  # Skip processed children
        else:
            # Elementary item
            size = calculate_field_size(field['pic'], field['comp'])
            for occur_idx in range(field['occurs']):
                alias = field['name']
                if field['occurs'] > 1:
                    alias += f"_{occur_idx + 1}"
                substr_list.append(
                    f"SUBSTR({record_name}, {position}, {size}) AS {alias}"
                )
                position += size
            i += 1

    return substr_list


def generate_substr_from_file(filename: str) -> str:
    """
    Read COBOL record definition from file and generate SUBSTR functions.

    Args:
        filename: Path to input file

    Returns:
        SUBSTR functions, one per line
    """
    with open(filename, 'r') as f:
        content = f.read()

    substr_list = parse_cobol_record(content)
    return '\n'.join(substr_list)


def generate_substr_from_text(text: str) -> str:
    """
    Generate SUBSTR functions from COBOL record definition text.

    Args:
        text: COBOL record definition as string

    Returns:
        SUBSTR functions, one per line
    """
    substr_list = parse_cobol_record(text)
    return '\n'.join(substr_list)


# Main function for command-line use
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python cobol_substr.py <input_file>")
        print("\nExample:")
        print("  python cobol_substr.py input1.txt")
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        result = generate_substr_from_file(input_file)
        print(result)
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)