import requests
import json
import sys
import re

DOMAIN_LISTS = [
    "https://raw.githubusercontent.com/mullvad/dns-blocklists/main/lists/doh/adblock/AdguardDNS",
    "https://raw.githubusercontent.com/cbuijs/adguarddns/main/Main/domains",
    "https://raw.githubusercontent.com/cbuijs/oisd/master/small/domains",
    "https://raw.githubusercontent.com/cbuijs/hagezi/main/lists/light/domains",
    "https://raw.githubusercontent.com/cbuijs/1hosts/main/Lite/domains",
    "https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/master/anti-ad-domains.txt",
    "https://raw.githubusercontent.com/jackszb/AWAvenue-Ads-Rule/main/AWAvenue-Ads-Rule-domains-cleaned.txt",
    "https://raw.githubusercontent.com/jackszb/Cats-Team/main/jiekouAD-domains-cleaned.txt",
    "https://raw.githubusercontent.com/cbuijs/blocklistproject/main/lists/ads/domains",
    "https://raw.githubusercontent.com/jackszb/merge-ads/main/httpdns.txt",
]

HEADERS = {
    "User-Agent": "GitHubActions-Adblock-Updater/1.0"
}

# ===== 新增：合法域名校验 =====
DOMAIN_PATTERN = re.compile(
    r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)"
    r"(?:\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*$"
)

def is_valid_domain(domain: str) -> bool:
    if not domain:
        return False
    if "://" in domain:
        return False
    if "/" in domain or "?" in domain or "#" in domain:
        return False
    if "_" in domain:
        return False
    return bool(DOMAIN_PATTERN.match(domain))


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

# ===== 新增：清除非法域名 =====
valid_domains = [d for d in all_domains if is_valid_domain(d)]
removed_count = len(all_domains) - len(valid_domains)

sorted_domains = sorted(valid_domains)

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
print(f"Removed {removed_count} invalid domains.")

if failed_sources:
    print("Warning: Some sources failed:")
    for u in failed_sources:
        print(" -", u)
