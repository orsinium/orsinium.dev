from pathlib import Path
import requests
import yaml

HEADERS = {'Accept': 'application/vnd.github.v3+json'}
URL = 'https://api.github.com/{org}/repos'
ORGS = [
    'users/orsinium',
    'orgs/orsinium-labs',
    'orgs/orsinium-archive',
    'orgs/life4',
    'orgs/dephell',
    'orgs/typeddjango',
]

result = dict()
for org in ORGS:
    print(org)
    response = requests.get(URL.format(org=org), headers=HEADERS)
    response.raise_for_status()
    for project in response.json():
        result[project['html_url']] = dict(
            stars=project['stargazers_count'],
            archived=project['archived'],
            description=project['description'],
            language=project['language'],
            updated_at=project['pushed_at'],
            license=(project['license'] or {}).get('spdx_id', ''),
        )

with Path('data', 'meta.yml').open('w') as stream:
    yaml.dump(data=result, stream=stream)
