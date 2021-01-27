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
            license=project['license'],
        )

with Path('data', 'meta.yml').open('w') as stream:
    yaml.dump(data=result, stream=stream)
