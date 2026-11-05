import os, re
from PIL import Image

root = os.path.dirname(os.path.abspath(__file__))
html = open(os.path.join(root, 'index.html'), encoding='utf-8').read()

paths = re.findall(r'assets/[a-zA-Z0-9_./]+\.(?:png|jpg|gif)', html)
for p in set(paths):
    if '{' in p:
        continue
    full = os.path.join(root, p.replace('/', os.sep))
    assert os.path.exists(full), f'Missing asset: {p}'
    im = Image.open(full)
    assert im.size[0] > 0 and im.size[1] > 0

cams = os.listdir(os.path.join(root, 'assets', 'cams'))
assert len(cams) == 49, f'Expected 49 cam frames, got {len(cams)}'
print(f'OK: {len(set(paths))} HTML paths + {len(cams)} camera/office frames verified.')
