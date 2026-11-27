---
layout: post
title: 해시 테이블과 충돌 처리
date: 2026-11-27 00:00:00 +0900
topic_id: ds-hash-table
categories:
- Data-Structure
tags:
- Hash
description: 해시 테이블은 키의 해시값으로 탐색할 범위를 줄이는 자료구조입니다. 서로 다른 키가 같은 위치로 모이는 충돌은 정상적으로 생길
  수 있어 동등성 검사도 필요합니다.
permalink: /topics/ds-hash-table/
github_url: https://github.com/js05157/cs-interview/blob/master/Data-Structure/Hash/ds-hash-table.md
content_type: cs
excerpt: ''
learning_format: five-section-v1
---

{% raw %}
## 정의

해시 테이블은 키의 해시값으로 탐색할 범위를 줄이는 자료구조입니다. 서로 다른 키가 같은 위치로 모이는 충돌은 정상적으로 생길 수 있어 동등성 검사도 필요합니다.

## 설명

충돌을 처리할 때 버킷에 항목을 연결하는 체이닝이나 테이블의 다른 칸을 탐사하는 개방 주소법을 사용할 수 있습니다. 개방 주소법의 삭제를 단순 빈칸으로 만들면 뒤쪽 키의 탐색을 끊을 수 있어 tombstone이나 재배치가 필요합니다.

좋은 분산과 적절한 부하율에서는 조회·추가가 기대 O(1)이지만 충돌 집중과 리사이즈 비용은 남습니다. 해시 계산 자체도 키 길이에 영향을 받을 수 있고, 정렬·범위 탐색은 기본 장점이 아닙니다.

equals가 같은 키는 같은 hashCode를 내야 하지만 해시가 같다고 같은 키는 아닙니다. 저장 뒤 동등성·해시에 사용하는 필드를 바꾸면 다시 찾지 못할 수 있습니다. 자료구조용 해시는 암호화나 비밀 보호 수단도 아닙니다.

## 적용 예시

동일한 hashCode를 가진 서로 다른 키를 넣고 각 값을 구분하는지 확인합니다. 충돌이 있어도 동등성 비교가 필요하다는 점을 보여 주며 공격 부하의 성능 측정은 아닙니다.

```java
import java.util.*;
public class CollisionDemo {
  record Key(int id) { @Override public int hashCode() { return 1; } }
  public static void main(String[] args) {
    Map<Key,String> map = new HashMap<>();
    map.put(new Key(1), "one"); map.put(new Key(2), "two");
    assert map.size() == 2;
    assert map.get(new Key(1)).equals("one");
    map.put(new Key(1), "updated");
    assert map.size() == 2 && map.get(new Key(1)).equals("updated");
  }
}
```

동일 hashCode를 강제로 부여한 두 키를 JDK 17에서 구분하는지 확인합니다. 충돌 공격에 대한 처리량·트리화 조건의 측정은 아닙니다.

## 정리

해시 테이블은 해시로 후보 범위를 좁힌 뒤 실제 키를 구분합니다. 충돌은 피할 수 없는 상황이므로 처리 규칙과 부하율이 중요합니다. 기대 상수 시간을 모든 입력의 최악 보장으로 해석하면 안 됩니다. 키의 동등성 상태를 안정되게 유지하고 재배치·메모리 비용도 고려해야 합니다.

## 꼬리 질문


<details class="cs-followup">
<summary>Q1. 두 키의 hashCode가 같으면 같은 값을 덮어쓸까요?</summary>
<div class="cs-followup-answer">
<p>해시가 같다는 사실만으로 같은 키는 아닙니다. equals 등 해당 구조의 동등성 계약으로 구분합니다.</p>
</div>
</details>

<details class="cs-followup">
<summary>Q2. 키를 넣은 뒤 hashCode에 쓰이는 필드를 바꾸면 왜 조회가 실패할 수 있을까요?</summary>
<div class="cs-followup-answer">
<p>저장된 위치와 새 해시로 탐색하는 위치가 어긋날 수 있기 때문입니다. 키의 동등성·해시 판단 상태는 저장 중 안정적으로 유지해야 합니다.</p>
</div>
</details>

---

**참고 자료**

- [Java 17 HashMap](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/HashMap.html)
- [MIT 6.006 강의 10](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/resources/mit6_006f11_lec10/)

{% endraw %}
