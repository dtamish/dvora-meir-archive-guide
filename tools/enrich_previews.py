#!/usr/bin/env python
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import json

path = Path(__file__).resolve().parents[1] / 'data' / 'archive.json'
data = json.loads(path.read_text(encoding='utf-8'))
commons = json.loads(path.with_name('commons-previews.json').read_text(encoding='utf-8'))
counts = {'youtube': 0, 'open-image': 0}
for item in data['items']:
    url = item.get('sourceUrl', '')
    if not url:
        continue
    if item.get('mediaGroup') == 'video':
        video_id = (parse_qs(urlparse(url).query).get('v') or [''])[0]
        if len(video_id) != 11:
            raise SystemExit(f"invalid YouTube id for {item['id']}: {url}")
        item['preview'] = {'kind':'youtube','thumbnailUrl':f'https://i.ytimg.com/vi/{video_id}/hqdefault.jpg','embedUrl':f'https://www.youtube-nocookie.com/embed/{video_id}','caption':f"YouTube · {item.get('source','מקור הסרט')}",'loadLabel':'ניגון הסרט באתר'}
        counts['youtube'] += 1
    elif item.get('mediaGroup') == 'stills' and item.get('rightsGroup') == 'open' and '/wiki/File:' in url:
        media = commons.get(url)
        if not media:
            raise SystemExit(f"missing Wikimedia preview metadata for {item['id']}: {url}")
        item['preview'] = {'kind':'open-image','thumbnailUrl':media['thumbnailUrl'].split('?',1)[0],'caption':f"Wikimedia Commons · {media['license']}",'loadLabel':'הצגת התמונה באתר'}
        counts['open-image'] += 1
data['meta']['previewCount'] = sum(counts.values())
data['meta']['inlinePlayableCount'] = counts['youtube']
path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(counts)
