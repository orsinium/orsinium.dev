import asyncio
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


async def query_org(org_name: str) -> dict[str, dict]:
    async with client as session:
        print(f'querying {org_name}')
        resp = await session.execute(
            document=gql(raw_query),
            variable_values={'org_name': org_name},
            operation_name='getRepos',
        )
        assert resp['organization']['repositories']['totalCount'] <= 100
        repos = resp['organization']['repositories']['nodes']

        # concurrently query info about all repos
        result = {}
        tasks = []
        for repo in repos:
            tasks.append(query_repo(session, org_name, repo['name']))
        print(f'awaiting additional info for {org_name} repositories')
        star_infos = await asyncio.gather(*tasks)
        for repo, stars in zip(repos, star_infos):
            result[repo['name']] = stars

        return result


async def query_repo(
    session,
    org_name: str,
    repo_name: str,
) -> dict[str, dict[str, object]]:
    result = {}
    cursor = None
    for pageno in range(1, 30):
        if pageno >= 4:
            print(f'querying page {pageno} for {org_name}/{repo_name}')
        page_content, cursor = await query_repo_page(
            session=session,
            org_name=org_name,
            repo_name=repo_name,
            cursor=cursor,
        )
        result.update(page_content)
        if cursor is None:
            break
    return result


async def query_repo_page(
    session,
    org_name: str,
    repo_name: str,
    cursor: str | None,
) -> tuple[dict[str, dict[str, object]], str | None]:
    resp = await session.execute(
        document=gql(raw_query),
        variable_values={
            'number_of_stargazers': 100,
            'org_name': org_name,
            'repo_name': repo_name,
            'cursor': cursor,
        },
        operation_name='getStargazers',
    )
    stargazers = resp['repository']['stargazers']
    users = {}
    for user in stargazers['nodes']:
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

    new_cursor = None
    if len(users) < stargazers['totalCount']:
        edges = stargazers['edges']
        if edges:
            new_cursor = edges[-1]['cursor']

    return users, new_cursor


async def main() -> None:
    result = {}
    orgs = ['life4', 'orsinium-labs']
    for org_name in orgs:
        print(org_name)
        result[org_name] = await query_org(org_name)
    with Path('data', 'stars.yml').open('w') as stream:
        yaml.dump(data=result, stream=stream)


if __name__ == '__main__':
    asyncio.run(main())
