import requests
import json
import sys

DOMAIN_LISTS = [
    "https://raw.githubusercontent.com/mullvad/dns-blocklists/main/lists/doh/adblock/AdguardDNS",
    "https://raw.githubusercontent.com/cbuijs/adguarddns/main/Main/domains",
    "https://raw.githubusercontent.com/cbuijs/oisd/master/small/domains",
    "https://raw.githubusercontent.com/cbuijs/hagezi/main/lists/light/domains",
    "https://raw.githubusercontent.com/cbuijs/1hosts/main/Lite/domains",
    "https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/master/anti-ad-domains.txt",
    "https://raw.githubusercontent.com/jackszb/AWAvenue-Ads-Rule/main/AWAvenue-Ads-Rule-domains-cleaned.txt",
    "https://raw.githubusercontent.com/jackszb/merge-ads/main/httpdns.txt",
]

HEADERS = {
    "User-Agent": "GitHubActions-Adblock-Updater/1.0"
}

all_domains = set()
failed_sources = []

for url in DOMAIN_LISTS:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()

        for line in resp.text.splitlines():
            line = line.strip()
            if line:
                all_domains.add(line)

        print(f"[OK] {url}")

    except Exception as e:
        print(f"[WARN] Failed to fetch {url}: {e}")
        failed_sources.append(url)

if not all_domains:
    print("[ERROR] No domains collected, aborting.")
    sys.exit(1)

sorted_domains = sorted(all_domains)

with open("ads-domains.txt", "w") as f:
    f.write("\n".join(sorted_domains) + "\n")

result = {
    "version": 3,
    "rules": [
        {
            "domain_suffix": sorted_domains
        }
    ]
}

with open("adblock.json", "w") as f:
    json.dump(result, f, indent=2)

print(f"Generated {len(sorted_domains)} domains.")
if failed_sources:
    print("Warning: Some sources failed:")
    for u in failed_sources:
        print(" -", u)
