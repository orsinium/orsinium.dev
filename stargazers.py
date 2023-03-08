import os
from pathlib import Path
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
import yaml

token = os.environ['GITHUB_TOKEN']
transport = AIOHTTPTransport(
    url="https://api.github.com/graphql",
    headers={'Authorization': f'bearer {token}'},
)
client = Client(transport=transport, fetch_schema_from_transport=True)
raw_query = Path('stargazers.gql').read_text()


def query_org(org_name: str) -> dict[str, dict]:
    resp = client.execute(
        document=gql(raw_query),
        variable_values={'org_name': org_name},
        operation_name='getRepos',
    )
    assert resp['organization']['repositories']['totalCount'] <= 100
    repos = resp['organization']['repositories']['nodes']
    result = {}
    for repo in repos:
        repo_name = repo['name']
        print(' ', repo_name)
        repo_info = query_repo(org_name, repo_name)
        result[repo_name] = repo_info
    return result


def query_repo(org_name, repo_name) -> dict[str, dict[str, object]]:
    resp = client.execute(
        document=gql(raw_query),
        variable_values={
            'number_of_stargazers': 100,
            'org_name': org_name,
            'repo_name': repo_name,
        },
        operation_name='getStargazers',
    )
    users = {}
    for user in resp['repository']['stargazers']['nodes']:
        if user['followers']['totalCount'] < 100:
            continue

        # parse top repositories of the user
        repos = []
        for subrepo in user['repositories']['nodes']:
            if subrepo['stargazerCount'] < 100:
                continue
            if subrepo['owner']['login'] != user['login']:
                continue
            repos.append(dict(
                name=subrepo['name'],
                stars=subrepo['stargazerCount'],
            ))

        # parse pinned repositories of the user
        pins = []
        for subrepo in user['pinnedItems']['nodes']:
            if not subrepo:
                continue
            if subrepo['stargazerCount'] < 100:
                continue
            pins.append(dict(
                name=subrepo['name'],
                owner=subrepo['owner']['login'],
                stars=subrepo['stargazerCount'],
            ))

        users[user['login']] = dict(
            followers=user['followers']['totalCount'],
            repos=repos,
            pins=pins,
        )
    return users


def main():
    result = {}
    for org_name in ['life4', 'orsinium-labs']:
        print(org_name)
        result[org_name] = query_org(org_name)
    with Path('data', 'stars.yml').open('w') as stream:
        yaml.dump(data=result, stream=stream)


if __name__ == '__main__':
    main()
