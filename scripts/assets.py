"""Copy only the selected topic's reviewed local diagram when that topic is published."""
import re
import hashlib
from pathlib import Path
import xml.etree.ElementTree as ET
from .core import MD,PublisherError,digest,safe_path


def asset_bytes(path):
    return path.read_bytes().replace(b"\r\n",b"\n")


def resolve_assets(root, private, topic, body):
    assets=[]
    for token in MD.parse(body):
        for image in token.children or []:
            if image.type!='image':continue
            src=image.attrGet('src') or ''
            if not src.startswith('cs-asset:'):continue
            relative=src[len('cs-asset:'):]
            # Each diagram belongs to the selected ID. Future topics cannot leak through a bundle.
            if relative != 'assets/diagrams/'+topic['topic_id']+'.svg':
                raise PublisherError('asset-outside-selected-topic')
            unresolved=Path(private)/relative
            if any(p.is_symlink() for p in (unresolved,*unresolved.parents)):
                raise PublisherError("asset-symlink-forbidden")
            path=safe_path(private,relative);data=asset_bytes(path)
            validate_svg(data)
            target='blog/'+relative
            assets.append({'source':relative,'target':target,'sha256':hashlib.sha256(data).hexdigest()})
            public='https://raw.githubusercontent.com/js05157/cs-interview/master/'+target+'?v='+hashlib.sha256(data).hexdigest()[:12]
            body=body.replace('('+src+')','('+public+')')
    return body,assets


def validate_svg(data):
    if len(data)>1_000_000 or b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper():
        raise PublisherError('unsafe-diagram-svg')
    try:node=ET.fromstring(data)
    except ET.ParseError:raise PublisherError('invalid-diagram-svg') from None
    if node.tag!='{http://www.w3.org/2000/svg}svg':raise PublisherError('invalid-diagram-svg-root')
    allowed={'svg','title','desc','g','rect','circle','ellipse','path','line','polyline','polygon','text','tspan','defs','marker'}
    for element in node.iter():
        if element.tag.split('}')[-1] not in allowed:raise PublisherError('unsafe-diagram-svg')
        for attr,value in element.attrib.items():
            if attr.lower().split('}')[-1].startswith('on') or attr.split('}')[-1] in {'href','style'}:
                raise PublisherError('unsafe-diagram-svg')
            if 'url(' in value and not re.fullmatch(r'url\(#[A-Za-z][\w-]*\)',value):raise PublisherError('unsafe-diagram-svg')


def copy_assets(root, private, assets, previous_assets=()):
    previous={a["target"]:a["sha256"] for a in previous_assets}
    for asset in assets:
        data=asset_bytes(safe_path(private,asset['source']))
        if hashlib.sha256(data).hexdigest()!=asset['sha256']:raise PublisherError('asset-source-changed')
        dest=safe_path(root,asset['target'])
        if dest.exists() and asset_bytes(dest)!=data:
            if hashlib.sha256(asset_bytes(dest)).hexdigest()!=previous.get(asset['target']):raise PublisherError('existing-asset-protected')
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)


def verify_assets(root, entry):
    for asset in entry.get('assets',[]):
        if asset.get('target')!='blog/assets/diagrams/'+entry['topic_id']+'.svg':
            raise PublisherError('asset-outside-selected-topic')
        path=safe_path(root,asset['target'])
        if not path.is_file() or hashlib.sha256(asset_bytes(path)).hexdigest()!=asset['sha256']:
            raise PublisherError('published-asset-changed-review-required')
