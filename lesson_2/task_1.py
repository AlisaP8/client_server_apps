import csv
import chardet


def get_data():

    os_prod_list = []
    os_name_list = []
    os_code_list = []
    os_type_list = []
    main_data = []
    result_data = ['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']

    for i in range(1, 4):
        with open(f'info_{i}.txt', 'rb') as file_test:
            data_bytes = file_test.read()
            result = chardet.detect(data_bytes)
            data = data_bytes.decode(result['encoding']).split('\n')

        for i in data:
            row_data = i.split(':')
            if 'Изготовитель системы' in row_data[0]:
                os_prod_list.append(row_data[1].strip())
            if 'Название ОС' in row_data[0]:
                os_name_list.append(row_data[1].strip())
            if 'Код продукта' in row_data[0]:
                os_code_list.append(row_data[1].strip())
            if 'Тип системы' in row_data[0]:
                os_type_list.append(row_data[1].strip())

    main_data.append(result_data)

    data_for_rows = [os_prod_list, os_name_list, os_code_list, os_type_list]

    for el in range(len(data_for_rows[0])):
        line = [row[el] for row in data_for_rows]
        main_data.append(line)

    return main_data


def write_to_csv(file_name):

    with open(file_name, 'w', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        for row in get_data():
            csv_writer.writerow(row)


write_to_csv('test.csv')
