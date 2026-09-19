#!/usr/bin/env bash
# Ping IndexNow-capable search engines (Bing, Yandex, Seznam) with the sitemap
# URLs so new/changed pages are fetched promptly instead of waiting on their
# normal crawl cadence. Safe to re-run; engines dedupe.
set -euo pipefail

KEY="512d1386689e4ecf83413329df74455e"
HOST="nativegate.dev"
SITEMAP="https://nativegate.dev/sitemap.xml"

command -v curl >/dev/null || { echo "curl required"; exit 1; }
command -v python3 >/dev/null || { echo "python3 required"; exit 1; }

# Pull locs out of the sitemap (local file keeps this script runnable before deploy).
SITE=$(python3 -c "
import xml.etree.ElementTree as ET
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
for u in ET.parse('marketing/sitemap.xml').getroot().findall('s:url',ns):
    print(u.find('s:loc',ns).text)
")

# The shared endpoint routes to Bing, Yandex, and Seznam in one call.
ENGINE="https://api.indexnow.org/indexnow"
COUNT=0
while IFS= read -r url; do
  curl -s -o /dev/null -w "%{http_code} $url\n" \
    -G "$ENGINE" \
    --data-urlencode "host=$HOST" \
    --data-urlencode "key=$KEY" \
    --data-urlencode "url=$url" || echo "ping failed for $url"
  COUNT=$((COUNT+1))
done <<EOF
$SITE
EOF
echo "requested $COUNT URLs via IndexNow ($ENGINE)"
