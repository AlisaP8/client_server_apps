import yaml

data = {
    '1': ['1', '2', '3'],
    '2': 2,
    '3': {
        '1': '1€',
        '2': '2Ћ',
        '3': '3Њ'
    }
}

with open('file.yaml', 'w', encoding='utf-8') as f_n:
    yaml.dump(data, f_n, default_flow_style=False, allow_unicode=True)

with open('file.yaml', 'r', encoding='utf-8') as f_n:
    yaml_data = yaml.load(f_n, Loader=yaml.SafeLoader)

if yaml_data == data:
    print('Данные совпали')
else:
    print('Данные не совпали')
