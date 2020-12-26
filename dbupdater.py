from re import compile
from openpyxl import load_workbook
from tinydb import TinyDB


def get_slices(sheet):
    row_start = 1
    while True:
        family_cell = sheet.cell(row=row_start, column=2)
        if family_cell.value == 'Quanta 5':
            row_old_start = row_start
            row_start = row_start + 24
            row_end = row_start - 2
        elif family_cell.value == 'Quanta 6':
            row_old_start = row_start
            row_start = row_start + 24
            row_end = row_start - 2
        elif family_cell.value == 'Quanta 70':
            row_old_start = row_start
            row_start = row_start + 15
            row_end = row_start - 2
        elif family_cell.value == 'InfiLINK XG 1000':
            row_old_start = row_start
            row_start = row_start + 15
            row_end = row_start - 2
        elif family_cell.value == 'InfiLINK XG 500':
            row_old_start = row_start
            row_start = row_start + 15
            row_end = row_start - 2
        elif family_cell.value == 'InfiLINK 2x2 PRO':
            row_old_start = row_start
            row_start = row_start + 18
            row_end = row_start - 2
        elif family_cell.value == 'InfiLINK 2x2 LITE':
            row_old_start = row_start
            row_start = row_start + 18
            row_end = row_start - 2
        elif family_cell.value is None:
            break
        yield row_old_start, row_end


def analyze_slice(start, end):
    capacity = {}
    availability = {'99.90': {}, '99.99': {}}
    for row in sheet.iter_rows(min_row=start, min_col=1, max_row=end, max_col=17):
        row_text = list(filter(lambda x: x is not None, [cell.value for cell in row]))
        if row_text[0] == 'Family':
            family = row_text[1]
        elif row_text[0] == 'Device':
            name = row_text[1]
        elif row_text[0] == 'Capacity, Mbps':
            capacity[f'{row_text[1]}'] = {f'MCS{id}': int(item) for id, item in enumerate(row_text[2:])}
        elif row_text[0] == 'Availability, 99.90%':
            availability['99.90'][row_text[1]] = {f'MCS{id}': float(item) for id, item in enumerate(row_text[2:])}
        elif row_text[0] == 'Availability, 99.99%':
            availability['99.99'][row_text[1]] = {f'MCS{id}': float(item) for id, item in enumerate(row_text[2:])}
    pattern = compile(r'([\w\d\.\/\-]+)(\+(MARS|MA|GENERIC))?')
    if ('-E' in name) or ('Um' in name) or ('Omx' in name) or ('Lmn' in name):
        device_type = 'external'
        model = pattern.search(name).group(1)
        cable = 'CAB-RF-1M'
    else:
        device_type = 'internal'
        model = pattern.search(name).group(1)
        cable = None

    return family, name, model, device_type, cable, capacity, availability


def write_db(table, family, name, model, device_type, cable, capacity, availability):
    result = {'Family': family,
              'Name': name,
              'Model': model,
              'Type': device_type,
              'RF Cable': cable,
              'Capacity': capacity,
              'Availability': availability
              }
    table.insert(result)


if __name__ == "__main__":
    db = TinyDB('devices.db')
    db.drop_tables()
    wb = load_workbook(filename='devices.xlsx')
    for sheet in wb:
        table = db.table(sheet.title)
        for slice in get_slices(sheet):
            device = analyze_slice(*slice)
            write_db(table, *device)
