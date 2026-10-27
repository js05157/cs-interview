"""Make a local-only synthetic post for Jekyll integration checks. No private content."""
import argparse
import shutil
from pathlib import Path

from .core import make_post, write_json


def build_fixture(destination):
    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError("fixture destination must be new")
    root = Path(__file__).resolve().parents[1]
    shutil.copytree(root / "blog", destination)
    body = '''# 합성 빌드 검증 문서

이 글은 비공개 대기열과 무관한 자동 테스트용 데이터입니다.

## 제목과 서식

**굵은 글씨**, `인라인 코드`, [GitHub](https://github.com/js05157/cs-interview).

- 첫 번째 항목
- 두 번째 항목

| 비교 | 값 |
| --- | --- |
| 합성 예제 | 검증 |

## 코드와 템플릿 문자

```java
class Fixture { String value = "{{ literal }}"; }
```
'''
    topic = dict(title_ko="합성 빌드 검증 문서", published_date="2020-01-01", topic_id="synthetic-build-fixture",
                 category="Java", subcategory="Testing", permalink="/topics/synthetic-build-fixture/",
                 github_url="https://github.com/js05157/cs-interview")
    (destination / "_posts/2020-01-01-synthetic-build-fixture.md").write_text(make_post(topic, body), encoding="utf-8")
    write_json(destination / "_data/publisher.json", dict(count=1, notion_url=""))
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--destination", required=True, type=Path)
    args = parser.parse_args()
    print(build_fixture(args.destination))
