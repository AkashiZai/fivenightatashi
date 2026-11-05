import os, re
from PIL import Image

root = os.path.dirname(os.path.abspath(__file__))

for page, cam_folder, expected_count in [
    ('index.html', 'assets/cams', 49),
    ('fnaf2.html', 'assets2/cams', 42),
]:
    html = open(os.path.join(root, page), encoding='utf-8').read()
    paths = re.findall(r'assets2?/[a-zA-Z0-9_./]+\.(?:png|jpg|gif)', html)
    for p in set(paths):
        if '{' in p:
            continue
        full = os.path.join(root, p.replace('/', os.sep))
        assert os.path.exists(full), f'Missing asset in {page}: {p}'
        im = Image.open(full)
        assert im.size[0] > 0 and im.size[1] > 0
    cams = os.listdir(os.path.join(root, cam_folder.replace('/', os.sep)))
    assert len(cams) == expected_count, f'Expected {expected_count} in {cam_folder}, got {len(cams)}'
    print(f'OK [{page}]: {len(set(paths))} paths + {len(cams)} frames verified.')
