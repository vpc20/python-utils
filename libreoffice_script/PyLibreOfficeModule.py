from scriptforge import CreateScriptService


def get_value_method(*args):
    doc = CreateScriptService("Calc")
    bas = CreateScriptService("Basic")

    sheet_name = doc.Sheets[0]  # dynamically get first sheet name

    # GetValue
    # Get the value(s) stored in the given range of cells as a single value, a 1 D array or a 2 D array.
    # All values are either doubles or strings.
    val = doc.getValue(f"{sheet_name}.A1")
    bas.MsgBox(f"Value : {val}")

    val = doc.getValue(f"{sheet_name}.A1:B1")
    bas.MsgBox(f"Value : {val}")

    val = doc.getValue(f"{sheet_name}.A1:B2")
    bas.MsgBox(f"Value : {val}")


def set_value_method(*args):
    doc = CreateScriptService("Calc")
    bas = CreateScriptService("Basic")

    sheet_name = doc.Sheets[0]  # dynamically get first sheet name

    # SetValue
    # Stores the given value in the specified range.The size of the modified area is equal to the size of the target range.
    # The method returns a string representing the modified area as a range of cells.
    doc.SetValue(f"{sheet_name}.A1", 2)
    doc.SetValue(f"{sheet_name}.A2:C2", (1, 2, 3))
    doc.SetValue(f"{sheet_name}.A3:D4", ((1, 2, 3, 4), (5, 6, 7, 8)))


def get_last_row(*args):
    doc = CreateScriptService("Calc")
    bas = CreateScriptService("Basic")

    sheet_name = doc.Sheets[0]  # dynamically get first sheet name
    last_row = doc.LastRow(sheet_name)

    bas.MsgBox(f"Last row: {last_row}")


def get_column_values(*args):
    doc = CreateScriptService("Calc")
    bas = CreateScriptService("Basic")

    sheet_name = doc.Sheets[0]  # dynamically get first sheet name
    last_row = doc.LastRow(sheet_name)

    for i in range(1, last_row + 1):
        val = doc.GetValue(f"{sheet_name}.A{i}")
        bas.MsgBox(f"Cell A{i} value: {val}")


def get_range_values(*args):
    doc = CreateScriptService("Calc")
    bas = CreateScriptService("Basic")

    sheet_name = doc.Sheets[0]  # dynamically get first sheet name
    last_row = doc.LastRow(sheet_name)

    for i in range(1, last_row + 1):
        val = doc.GetValue(f"{sheet_name}.A{i}")
        bas.MsgBox(f"Cell A{i} value: {val}")
        val = doc.GetValue(f"{sheet_name}.B{i}")
        bas.MsgBox(f"Cell B{i} value: {val}")


def fill_range(*args):
    bas = CreateScriptService("Basic")

    try:
        doc = CreateScriptService("Calc")
        sheet_name = doc.Sheets[0]

        # Fill A1:A10 with squares
        for i in range(1, 11):
            doc.SetValue(f"{sheet_name}.A{i}", i * i)

        # Read back as 1D tuple (single column)
        data = doc.GetValue(f"{sheet_name}.A1:A10")

        # Access directly — no second index needed
        first = data[0]
        last = data[9]

        bas.MsgBox(f"First: {first}, Last: {last}")

    except Exception as e:
        bas.MsgBox(f"Error: {str(e)}")


def manage_sheets(*args):
    doc = CreateScriptService("Calc")

    # List all sheet names
    sheets = doc.Sheets  # returns a tuple of sheet names

    # Create a new sheet
    doc.InsertSheet("MyNewSheet")

    # Copy a sheet
    doc.CopySheet("Sheet1", "Sheet1_Backup")

    # Remove a sheet
    # doc.RemoveSheet("MyNewSheet")

    bas = CreateScriptService("Basic")
    bas.MsgBox(f"Sheets: {sheets}")


def format_cells(*args):
    bas = CreateScriptService("Basic")

    try:
        doc = CreateScriptService("Calc")
        sheet_name = doc.Sheets[0]

        # Write header
        doc.SetValue(f"{sheet_name}.A1", "Sales Report")

        # Get UNO cell object via XCellRange
        cell = doc.XCellRange(f"{sheet_name}.A1")

        # Background color and text color (UNO properties)
        cell.CellBackColor = 0x4472C4  # blue background
        cell.CharColor = 0xFFFFFF  # white text
        cell.CharWeight = 150  # bold (com.sun.star.awt.FontWeight.BOLD = 150)
        cell.CharHeight = 14  # font size

        bas.MsgBox("Formatting applied!")

    except Exception as e:
        bas.MsgBox(f"Error: {str(e)}")


def format_range(*args):
    bas = CreateScriptService("Basic")

    try:
        doc = CreateScriptService("Calc")
        sheet_name = doc.Sheets[0]

        # Write some data
        doc.SetArray(f"{sheet_name}.A1", [["Name", "Sales", "Region"]])

        # Get UNO range object for the header row
        header_range = doc.XCellRange(f"{sheet_name}.A1:C1")
        header_range.CellBackColor = 0x4472C4  # blue
        header_range.CharColor = 0xFFFFFF  # white text
        header_range.CharWeight = 150  # bold
        header_range.CharHeight = 16  # font size

        # Format a data range differently
        data_range = doc.XCellRange(f"{sheet_name}.A2:C10")
        data_range.CellBackColor = 0xDDEEFF  # light blue

        bas.MsgBox("Range formatting done!")

    except Exception as e:
        bas.MsgBox(f"Error: {str(e)}")


def ask_user(*args):
    bas = CreateScriptService("Basic")

    # Simple input box
    name = bas.InputBox("Enter your name:", "User Input", "World")

    doc = CreateScriptService("Calc")
    doc.SetValue("Sheet1.A1", f"Hello, {name}!")

    bas.MsgBox(f"Written to A1: Hello, {name}!")


def get_cell_by_letter_number(*args):
    bas = CreateScriptService("Basic")

    try:
        doc = CreateScriptService("Calc")
        sheet_name = doc.Sheets[0]

        row, col = 3, 2  # e.g. row 3, col 2

        # Build cell address string like "Sheet1.C3"
        # SF_Calc uses column letters, so convert col number to letter
        col_letter = chr(64 + col)  # 1=A, 2=B, 3=C ...
        cell_ref = f"{sheet_name}.{col_letter}{row}"

        # Read / write using the ref
        doc.SetValue(cell_ref, 999)
        val = doc.GetValue(cell_ref)

        bas.MsgBox(f"Cell {cell_ref} = {val}")

    except Exception as e:
        bas.MsgBox(f"Error: {str(e)}")


def get_cell_by_rowcol(*args):
    bas = CreateScriptService("Basic")

    try:
        doc = XSCRIPTCONTEXT.getDocument()
        sheet = doc.getSheets().getByIndex(0)

        # Write a numeric value to row=0, col=0 (cell A1)
        cell = sheet.getCellByPosition(0, 0)  # col first, then row
        cell.setValue(42)
        val = cell.getValue()
        bas.MsgBox(f"Numeric cell A1 = {val}")

        # Write a string to row=1, col=0 (cell A2)
        cell = sheet.getCellByPosition(0, 1)
        cell.setString("Hello ScriptForge")
        txt = cell.getString()
        bas.MsgBox(f"String cell A2 = {txt}")

        # Write a formula to row=2, col=0 (cell A3) — depends on A1
        cell = sheet.getCellByPosition(0, 2)
        cell.setFormula("=A1+1")
        result = cell.getValue()
        bas.MsgBox(f"Formula cell A3 =A1+1 = {result}")

    except Exception as e:
        bas.MsgBox(f"Error: {str(e)}")
