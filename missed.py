from pathlib import Path
import yaml

with Path('data', 'meta.yml').open('r') as stream:
    all_links = set(yaml.safe_load(stream))

listed_links = set()
with Path('data', 'projects.yml').open('r') as stream:
    for lang in yaml.safe_load(stream):
        for item in lang['items']:
            listed_links.add(item['link'])

print(*sorted(all_links - listed_links), sep='\n')
