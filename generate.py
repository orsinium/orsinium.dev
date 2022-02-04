from typing import Any, Dict, Iterator, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

import yaml
from jinja2 import Environment, FileSystemLoader


env = Environment(
    loader=FileSystemLoader('templates'),
    extensions=['jinja2.ext.loopcontrols', 'jinja2_markdown.MarkdownExtension'],
)

threshold = (datetime.now() - timedelta(days=450)).isoformat()
buttons = yaml.safe_load(Path('data', 'buttons.yml').open())
menu = yaml.safe_load(Path('data', 'names.yml').open())
meta = yaml.safe_load(Path('data', 'meta.yml').open())


@dataclass
class Tag:
    name: str
    count: int

    @property
    def id(self):
        return 'tag-' + self.name


@dataclass
class Projects:
    items: List[Dict[str, Any]]

    @property
    def tags(self) -> Iterator[Tag]:
        tags: Counter[str] = Counter()
        for item in self.items:
            tags.update(item.get('tags', []))
        for name, count in tags.most_common():
            yield Tag(name=name, count=count)

    def __iter__(self):
        yield from self.items


WRAPPERS = dict(
    projects=Projects,
)


def generate_website() -> None:
    titles = {item['slug']: item['name'] for item in menu if 'slug' in item}
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
        wrapper = WRAPPERS.get(name)
        if wrapper is not None:
            data = wrapper(data)
        content = template.render(
            items=data,
            buttons=buttons,
            menu=menu,
            meta=meta,
            threshold=threshold,
            title=titles[name] if name != 'index' else None,
        )
        Path('public', name).with_suffix('.html').write_text(content)


def generate_cv() -> None:
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


if __name__ == '__main__':
    generate_website()
    generate_cv()
