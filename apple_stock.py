import sys, re, requests
from bs4 import BeautifulSoup

URL = "https://finance.yahoo.com/quote/AAPL/history?p=AAPL"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_html(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        sys.exit(f"Error fetching {url}: {e}")

def clean(txt):
    return re.sub(r"\s+", " ", txt).strip()

def main():
    html = fetch_html(URL)
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one('table[data-test="historical-prices"]')
    if not table:
        table = soup.find('table')
    if not table:
        sys.exit("Could not find the historical prices table.")
    thead = table.find('thead')
    if not thead:
        sys.exit("Could not find table header.")
    headers = [clean(th.get_text()) for th in thead.find_all('th')]
    def find_idx(cands):
        for i, h in enumerate(headers):
            for c in cands:
                if h.lower().startswith(c):
                    return i
        return None
    idx_date = find_idx(["date"])
    idx_close = find_idx(["close", "close/last"])
    if idx_date is None or idx_close is None:
        sys.exit(f"Expected columns not found. Headers: {headers}")
    tbody = table.find('tbody')
    if not tbody:
        sys.exit("Could not find table body.")
    rows = tbody.find_all('tr', recursive=False)
    if not rows:
        sys.exit("No rows found.")
    print("AAPL Historical Prices — Date and Close (Yahoo Finance)")
    print("-" * 60)
    printed = 0
    for tr in rows:
        cells = tr.find_all('td')
        if len(cells) <= max(idx_date, idx_close):
            continue
        date_txt = clean(cells[idx_date].get_text())
        close_txt = clean(cells[idx_close].get_text())
        if "Dividend" in close_txt or not date_txt or not close_txt:
            continue
        print(f"{date_txt}: {close_txt}")
        printed += 1
    if printed == 0:
        sys.exit("Parsed 0 rows (the page may have changed).")

if __name__ == "__main__":
    main()
