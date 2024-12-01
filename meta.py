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
    for page in range(1, 4):
        if page > 1:
            print(f'  page {page}')
        response = requests.get(
            URL.format(org=org),
            params=dict(per_page=100, page=page),
            headers=HEADERS,
        )
        response.raise_for_status()
        org_projects = response.json()
        for project in org_projects:
            result[project['html_url']] = dict(
                stars=project['stargazers_count'],
                archived=project['archived'],
                description=project['description'],
                language=project['language'],
                updated_at=project['pushed_at'].split('T')[0],
                license=(project['license'] or {}).get('spdx_id', ''),
            )
        if len(org_projects) < 100:
            break

with Path('data', 'meta.yml').open('w') as stream:
    yaml.dump(data=result, stream=stream)
