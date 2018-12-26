import yaml

data = yaml.load(open('data.yml').read())

for section in data.values():
    for block in section:
        if 'info' not in block:
            continue
        text = block['info'].replace('\n', ' ')
        while '  ' in text:
            text = text.replace('  ', ' ')
        print(text)
        print()

print('-' * 80)

for section in data['skills']:
    for block in section['content']:
        if 'info' not in block:
            continue
        text = block['info'].replace('\n', ' ')
        while '  ' in text:
            text = text.replace('  ', ' ')
        print(text)
        print()
