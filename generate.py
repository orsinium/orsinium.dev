import yaml
from jinja2 import Environment, FileSystemLoader
from pathlib import Path


env = Environment(
    loader=FileSystemLoader('templates'),
    extensions=['jinja2.ext.loopcontrols', 'jinja2_markdown.MarkdownExtension'],
)

buttons = yaml.load(Path('data', 'buttons.yml').open())

for data_path in Path('data').iterdir():
    data = yaml.load(data_path.open())
    name = data_path.stem
    if name in {'buttons'}:
        continue
    template_path = Path('templates', name).with_suffix('.html.j2')
    if not template_path.exists():
        print('no template', str(template_path))
        continue
    template = env.get_template(template_path.name)
    content = template.render(items=data, buttons=buttons)
    Path('public', name).with_suffix('.html').write_text(content)
