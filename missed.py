from pathlib import Path
import yaml

IGNORE = {
    'https://github.com/dephell/dephell_homepage',
    'https://github.com/orsinium-archive/djcore',
    'https://github.com/orsinium-archive/kaspersky-ctf-scada-write-up',
    'https://github.com/orsinium-archive/likes',
    'https://github.com/orsinium-archive/requests-connection',
    'https://github.com/orsinium-archive/skyeng',
    'https://github.com/orsinium-archive/vksploit',
    'https://github.com/orsinium-archive/workout',
    'https://github.com/orsinium-labs/memcached',
    'https://github.com/orsinium-labs/turtle',
    'https://github.com/orsinium/bowler-py35',
    'https://github.com/orsinium/fissix-py35',
    'https://github.com/orsinium/forks',
    'https://github.com/orsinium/mlcourse',
    'https://github.com/orsinium/my-go',
    'https://github.com/orsinium/orsinium.dev',
    'https://github.com/typeddjango/django-mypy-plugin',
    'https://github.com/typeddjango/django-stubs',
    'https://github.com/typeddjango/djangorestframework-stubs',
    'https://github.com/typeddjango/pytest-mypy-plugins',
}

with Path('data', 'meta.yml').open('r') as stream:
    all_links = set(yaml.safe_load(stream))


listed_links = IGNORE
with Path('data', 'projects.yml').open('r') as stream:
    for lang in yaml.safe_load(stream):
        for item in lang['items']:
            listed_links.add(item['link'])

print(*sorted(all_links - listed_links), sep='\n')
