"""
Inspecciona los workbooks abiertos en Excel y muestra su estructura.
Ejecutar en Windows PowerShell: python inspect_excel.py
"""
import win32com.client
import pythoncom

pythoncom.CoInitialize()

try:
    excel = win32com.client.GetObject(Class="Excel.Application")
except Exception:
    print("ERROR: No hay instancia de Excel abierta.")
    print("Abrir Excel con un libro antes de ejecutar este script.")
    exit(1)

print("=" * 60)
print("  Excel Inspector - Galleguimetro")
print("=" * 60)

for wb in excel.Workbooks:
    print(f"\nWorkbook: {wb.Name}")
    print(f"  Path: {wb.FullName}")
    print(f"  Hojas: {wb.Sheets.Count}")

    for sheet in wb.Sheets:
        used = sheet.UsedRange
        rows = used.Rows.Count
        cols = used.Columns.Count
        print(f"\n  Hoja: '{sheet.Name}' ({rows} filas x {cols} columnas)")

        if rows > 0 and cols > 0:
            # Headers (fila 1)
            headers = []
            for c in range(1, min(cols + 1, 26)):
                val = sheet.Cells(1, c).Value
                col_letter = chr(64 + c) if c <= 26 else f"col{c}"
                if val:
                    headers.append(f"{col_letter}='{val}'")
            print(f"    Headers: {', '.join(headers)}")

            # Primera fila de datos (fila 2)
            if rows > 1:
                sample = []
                for c in range(1, min(cols + 1, 26)):
                    val = sheet.Cells(2, c).Value
                    col_letter = chr(64 + c) if c <= 26 else f"col{c}"
                    if val is not None:
                        sample.append(f"{col_letter}={val}")
                print(f"    Fila 2:  {', '.join(sample)}")

            # Contar filas con datos en col A
            data_rows = 0
            for r in range(2, min(rows + 1, 1000)):
                if sheet.Cells(r, 1).Value:
                    data_rows += 1
                else:
                    break
            print(f"    Filas con datos: ~{data_rows}")

print("\n" + "=" * 60)
print("Usa esta informacion para ajustar bridge_config.json")
print("=" * 60)
