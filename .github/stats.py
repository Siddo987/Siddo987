# Writes this year's commits and projects into README.md between <!-- stats --> and <!-- /stats -->
import datetime, json, os, re, urllib.request

QUERY = '''query($from: DateTime!) { viewer {
  contributionsCollection(from: $from) {
    totalCommitContributions
    commitContributionsByRepository(maxRepositories: 100) { repository { name } }
  }
} }'''


def sentence(viewer):
    c = viewer['contributionsCollection']
    # the profile repo itself is not a project
    projects = [r for r in c['commitContributionsByRepository'] if r['repository']['name'] != 'Siddo987']
    commits = f"{c['totalCommitContributions']:,}".replace(',', '.')
    return f'Dieses Jahr sind dabei schon **{commits} Commits** in **{len(projects)} Projekten** zusammengekommen.'


year = datetime.date.today().year
req = urllib.request.Request(
    'https://api.github.com/graphql',
    data=json.dumps({'query': QUERY, 'variables': {'from': f'{year}-01-01T00:00:00Z'}}).encode(),
    headers={'Authorization': f"bearer {os.environ['GH_TOKEN']}"})
viewer = json.load(urllib.request.urlopen(req))['data']['viewer']

with open('README.md') as f:
    readme = f.read()
readme, found = re.subn(r'(<!-- stats -->).*?(<!-- /stats -->)', lambda m: m[1] + sentence(viewer) + m[2], readme, flags=re.S)
assert found == 1, 'stats markers missing in README.md'
with open('README.md', 'w') as f:
    f.write(readme)
