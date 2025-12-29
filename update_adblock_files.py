import requests
import json

DOMAIN_LISTS = [
    "https://raw.githubusercontent.com/mullvad/dns-blocklists/main/lists/doh/adblock/AdguardDNS",
    "https://raw.githubusercontent.com/cbuijs/oisd/master/small/domains"
]

# 下载并合并域名列表
with open('ads-domains.txt', 'w') as outfile:
    for url in DOMAIN_LISTS:
        response = requests.get(url)
        if response.status_code == 200:
            # 过滤空行和注释行
            lines = response.text.splitlines()
            for line in lines:
                if line.strip() and not line.startswith("#"):
                    outfile.write(line.strip() + "\n")

# 读取 ads-domains.txt 生成 adblock.json
with open('ads-domains.txt', 'r') as f:
    domain_list = [line.strip() for line in f.readlines() if line.strip()]

result = {
    "version": 3,
    "rules": [
        {
            "domain_suffix": domain_list
        }
    ]
}

with open('adblock.json', 'w') as json_file:
    json.dump(result, json_file, indent=2)

print("ads-domains.txt and adblock.json generated.")
