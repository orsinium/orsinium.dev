import yaml
from jinja2 import Environment, FileSystemLoader
from pathlib import Path


env = Environment(
    loader=FileSystemLoader('templates'),
    extensions=['jinja2.ext.loopcontrols', 'jinja2_markdown.MarkdownExtension'],
)

buttons = yaml.load(Path('data', 'buttons.yml').open())
menu = yaml.load(Path('data', 'names.yml').open())
titles = {item['slug']: item['name'] for item in menu}
for item in menu:
    if 'link' not in item:
        item['link'] = './{}.html'.format(item['slug'])

for data_path in Path('data').iterdir():
    data = yaml.load(data_path.open())
    name = data_path.stem
    if name in {'buttons', 'names'}:
        continue
    template_path = Path('templates', name).with_suffix('.html.j2')
    if not template_path.exists():
        template_path = Path('templates', 'base.html.j2')
    template = env.get_template(template_path.name)
    content = template.render(
        items=data,
        buttons=buttons,
        menu=menu,
        title=titles[name] if name != 'index' else None,
    )
    Path('public', name).with_suffix('.html').write_text(content)
