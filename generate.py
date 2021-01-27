import yaml
from jinja2 import Environment, FileSystemLoader
from pathlib import Path


env = Environment(
    loader=FileSystemLoader('templates'),
    extensions=['jinja2.ext.loopcontrols', 'jinja2_markdown.MarkdownExtension'],
)

buttons = yaml.safe_load(Path('data', 'buttons.yml').open())
menu = yaml.safe_load(Path('data', 'names.yml').open())
meta = yaml.safe_load(Path('data', 'meta.yml').open())

titles = {item['slug']: item['name'] for item in menu}
for item in menu:
    if 'link' not in item:
        item['link'] = './{}.html'.format(item['slug'])

for data_path in Path('data').iterdir():
    name = data_path.stem
    if name in {'buttons', 'names', 'meta'}:
        continue
    template_path = Path('templates', name).with_suffix('.html.j2')
    if not template_path.exists():
        template_path = Path('templates', 'base.html.j2')
    template = env.get_template(template_path.name)
    data = yaml.safe_load(data_path.open())
    content = template.render(
        items=data,
        buttons=buttons,
        menu=menu,
        meta=meta,
        title=titles[name] if name != 'index' else None,
    )
    Path('public', name).with_suffix('.html').write_text(content)


output_name = 'cv.html'
template = env.get_template(output_name + '.j2')
context = dict()
for data_path in Path('data').iterdir():
    name = data_path.stem
    if name in {'buttons', 'names'}:
        continue
    context[name] = yaml.safe_load(data_path.open())
content = template.render(**context)
Path('public', output_name).write_text(content)
