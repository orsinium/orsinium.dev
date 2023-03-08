from __future__ import annotations

from typing import Any, Iterator
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

import yaml
from jinja2 import Environment, FileSystemLoader
from functools import cached_property


env = Environment(
    loader=FileSystemLoader('templates'),
    extensions=['jinja2.ext.loopcontrols',
                'jinja2_markdown.MarkdownExtension'],
)

threshold = (datetime.now() - timedelta(days=450)).isoformat()
buttons = yaml.safe_load(Path('data', 'buttons.yml').open())
menu = yaml.safe_load(Path('data', 'names.yml').open())
meta = yaml.safe_load(Path('data', 'meta.yml').open())
TAGS = yaml.safe_load(Path('data', 'tags.yml').open())


@dataclass
class Tag:
    name: str
    count: int = 0
    show: bool = True
    icon_fa: str = ''
    icon_mn: str = ''
    important: bool = False

    @property
    def id(self):
        return 'tag_' + self.name


@dataclass
class Project:
    data: dict[str, Any]

    def __getitem__(self, name):
        return self.data[name]

    def __getattr__(self, name):
        return getattr(self.data, name)

    def __contains__(self, name):
        return name in self.data

    @cached_property
    def name(self) -> str:
        name = self.data.get('name')
        if name:
            return name
        return self.data['link'].split('/')[-1]

    @cached_property
    def info(self):
        info = self.data.get('info', '').rstrip()
        if not info and self.meta:
            info = self.meta.get('description', '')
        if info and info[-1] not in '.?!':
            info = info + '.'
        return info

    @cached_property
    def meta(self) -> dict[str, Any] | None:
        return meta.get(self.data.get('link'))

    @property
    def stars(self):
        if self.meta is None:
            return 0
        return self.meta['stars']

    @property
    def archived(self):
        if self.meta is None:
            return False
        return self.meta['archived']

    @property
    def experimental(self):
        if self.meta is None:
            return False
        return 'orsinium-labs' in self.data['link']

    @property
    def stale(self):
        if self.archived or self.meta is None:
            return False
        return self.meta['updated_at'] < threshold

    @property
    def popular(self):
        return self.stars > 20

    @property
    def cli(self) -> bool:
        if 'cli' in self.data.get('tags', []):
            return True
        if self.meta:
            desc = self.meta['description'] or ''
            if 'CLI' in desc:
                return True
        desc = self.data.get('description', '')
        if 'CLI' in desc:
            return True
        return False

    @property
    def oss(self) -> bool:
        return 'https://github.com/' in self.data.get('link', '')

    @cached_property
    def tags(self) -> list[Tag]:
        tags: list[Tag] = []

        if 'lang' in self.data:
            tags.append(Tag(self.data['lang'], show=False))
        if 'https://t.me/s/' in self.data.get('link', ''):
            tags.append(Tag('channel'))
        if self.oss:
            tags.append(Tag('oss', show=False))
        if 'flake8' in self.name:
            tags.append(Tag('flake8'))

        if self.meta:
            lang: str = self.meta['language']
            if lang:
                lang = lang.lower().replace('jupyter notebook', 'jupyter')
                tags.append(Tag(lang))
            if self.popular:
                tags.append(Tag('popular', show=False))
            if self.archived:
                tags.append(Tag('archived', show=False))
            if self.stale:
                tags.append(Tag('stale', show=False))
            if self.cli:
                tags.append(Tag('cli'))

        tag_names = {t.name for t in tags}
        for t in self.data.get('tags', []):
            if t in tag_names:
                continue
            tag_names.add(t)
            tags.append(Tag(t))
        return tags

    @property
    def tag_ids(self):
        return [tag.id for tag in self.tags]


@dataclass
class Projects:
    items: list[dict[str, Any]]

    @cached_property
    def tags(self) -> Iterator[Tag]:
        tags: Counter[str] = Counter()
        for item in self:
            tags.update(tag.name for tag in item.tags)
        for name, count in tags.most_common():
            tag_info = TAGS.get(name, {})
            yield Tag(name=name, count=count, **tag_info)

    def __iter__(self):
        for item in self.items:
            yield Project(item)

    @property
    def count(self):
        return len(self.items)

    @property
    def oss_count(self) -> int:
        return sum(item.oss for item in self)


@dataclass
class Repo:
    owner: str
    name: str
    stars: int

    @property
    def url(self) -> str:
        return f'https://github.com/{self.owner}/{self.name}'


@dataclass
class User:
    name: str
    followers: int
    repos: list[Repo]  # top repos of the user
    stars: list[Repo]  # repos that the user starred

    @cached_property
    def top_repo(self) -> Repo | None:
        if not self.repos:
            return None
        repo = self.repos[0]
        if repo.stars < 1000:
            return None
        return repo

    @property
    def url(self) -> str:
        return f'https://github.com/{self.name}'


@dataclass
class Stars:
    items: dict[str, dict[str, dict[str, dict[str, Any]]]]

    @property
    def top_users(self) -> Iterator[User]:
        for user in self.users:
            if user.followers < 400:
                continue
            yield user

    @cached_property
    def users(self) -> list[User]:
        grouped: dict[str, User] = {}
        for star in self.stars:
            user = grouped.setdefault(star['user'].name, star['user'])
            user.stars.append(Repo(
                owner=star['org_name'],
                name=star['repo_name'],
                stars=0,
            ))
        return sorted(
            grouped.values(),
            key=lambda u: u.followers,
            reverse=True,
        )

    @property
    def stars(self) -> Iterator[dict]:
        for org_name, repos in self.items.items():
            for repo_name, users in repos.items():
                for user_name, user_info in users.items():
                    user = User(
                        name=user_name,
                        followers=user_info['followers'],
                        repos=[
                            Repo(**r, owner=user_name)
                            for r in user_info['repos']
                        ],
                        stars=[],
                    )
                    yield dict(
                        repo_name=repo_name,
                        org_name=org_name,
                        user=user,
                    )


WRAPPERS = dict(
    projects=Projects,
    stars=Stars,
)


def generate_website() -> None:
    titles = {item['slug']: item['name'] for item in menu if 'slug' in item}
    for item in menu:
        if 'link' not in item:
            item['link'] = './{}.html'.format(item['slug'])

    for data_path in Path('data').iterdir():
        name = data_path.stem
        if name in {'buttons', 'names', 'meta', 'tags'}:
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
        data = yaml.safe_load(data_path.open())
        wrapper = WRAPPERS.get(name)
        if wrapper is not None:
            data = wrapper(data)
        context[name] = data
    content = template.render(**context)
    Path('public', output_name).write_text(content)


if __name__ == '__main__':
    generate_website()
    generate_cv()
