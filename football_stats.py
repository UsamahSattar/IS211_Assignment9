import sys, re, requests
from bs4 import BeautifulSoup

URL = "https://www.cbssports.com/nfl/stats/player/scoring/nfl/regular/all/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_html(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        sys.exit(f"Error fetching {url}: {e}")

def find_table(soup):
    table = soup.select_one('table.TableBase-table')
    if table:
        return table
    tables = soup.find_all('table')
    return tables[0] if tables else None

def header_map(th):
    return re.sub(r"\s+", " ", th.get_text(strip=True)).upper()

def main():
    html = fetch_html(URL)
    soup = BeautifulSoup(html, "html.parser")
    table = find_table(soup)
    if not table:
        sys.exit("Could not locate stats table on the page.")
    thead = table.find('thead')
    if not thead:
        sys.exit("Could not locate table header.")
    headers = [header_map(th) for th in thead.find_all('th')]
    def idx_of(names):
        for n in names:
            if n in headers:
                return headers.index(n)
        return None
    idx_player = idx_of(["PLAYER"])
    idx_team = idx_of(["TEAM"])
    idx_pos = idx_of(["POS", "POSITION"])
    idx_td = idx_of(["TD", "TOT TD", "TOTAL TD"])
    if idx_player is None or idx_td is None:
        sys.exit(f"Expected columns not found. Got headers: {headers}")
    tbody = table.find('tbody')
    if not tbody:
        sys.exit("Could not locate table body.")
    rows = tbody.find_all('tr', recursive=False)
    if not rows:
        sys.exit("No data rows found.")
    print("Top 20 NFL Touchdowns (Regular Season) — CBS Sports")
    print("-" * 60)
    count = 0
    for tr in rows:
        if count >= 20:
            break
        tds = tr.find_all(['td', 'th'])
        if not tds or len(tds) < max(idx_player, idx_td) + 1:
            continue
        player = tds[idx_player].get_text(strip=True)
        team = tds[idx_team].get_text(strip=True) if idx_team is not None else ""
        pos = tds[idx_pos].get_text(strip=True) if idx_pos is not None else ""
        td = tds[idx_td].get_text(strip=True)
        if not player or player.upper() == "PLAYER":
            continue
        count += 1
        print(f"{count:2}. {player} ({pos or '—'}, {team or '—'}) TD: {td}")
    if count == 0:
        sys.exit("No player rows parsed — the page layout may have changed.")

if __name__ == "__main__":
    main()
