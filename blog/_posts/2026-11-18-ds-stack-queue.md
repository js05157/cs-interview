---
layout: post
title: 스택과 큐
date: 2026-11-18 00:00:00 +0900
topic_id: ds-stack-queue
categories:
- Data-Structure
tags:
- Linear
description: 스택은 마지막에 넣은 것을 먼저 꺼내는 LIFO 규칙입니다. FIFO 큐는 먼저 넣은 것을 먼저 꺼내며, 둘은 내부 배열이나
  노드 모양보다 처리 순서를 설명합니다.
permalink: /topics/ds-stack-queue/
github_url: https://github.com/js05157/cs-interview/blob/master/Data-Structure/Linear/ds-stack-queue.md
content_type: cs
excerpt: ''
learning_format: five-section-v1
---

{% raw %}
## 정의

스택은 마지막에 넣은 것을 먼저 꺼내는 LIFO 규칙입니다. FIFO 큐는 먼저 넣은 것을 먼저 꺼내며, 둘은 내부 배열이나 노드 모양보다 처리 순서를 설명합니다.

## 설명

Deque의 같은 앞쪽에 push/pop하면 스택이 되고, 뒤에 offerLast하고 앞에서 pollFirst하면 FIFO 큐가 됩니다. Java ArrayDeque는 양 끝의 위치를 관리하고 공간이 부족하면 확장합니다.

poll의 빈 상태 반환은 null이고 remove는 예외를 던집니다. ArrayDeque는 null 원소를 허용하지 않지만 다른 Queue의 계약은 확인해야 합니다. PriorityQueue는 우선순위대로 꺼내므로 모든 Queue 구현을 FIFO라고 단정하지 않습니다.

일반 양 끝 연산은 분할 상환 O(1)이지만 임의 값 검색·삭제는 O(n)입니다. ArrayDeque는 공유 수정에 안전한 동기화 구현이 아니며, 서버 큐에는 처리 한도와 거절·백프레셔도 필요합니다.

## 적용 예시

같은 Deque API로 LIFO/FIFO와 빈 상태의 결과를 확인합니다. DFS는 스택, BFS는 FIFO 큐가 필요한 상황의 대표적 예입니다.

```java
import java.util.*;
public class DequeDemo {
  public static void main(String[] args) {
    Deque<Integer> stack = new ArrayDeque<>();
    stack.push(1); stack.push(2);
    assert stack.pop() == 2 && stack.pop() == 1;
    Deque<Integer> queue = new ArrayDeque<>();
    queue.offerLast(1); queue.offerLast(2);
    assert queue.pollFirst() == 1 && queue.pollFirst() == 2;
    assert queue.pollFirst() == null;
  }
}
```

JDK 17 실행으로 FIFO/LIFO와 빈 큐 반환을 확인합니다. 여러 생산자·소비자 환경은 이 비동기화 구현으로 검증하지 않습니다.

## 정리

스택과 FIFO 큐는 원소를 꺼내는 순서가 다릅니다. Deque는 사용하는 끝과 메서드에 따라 두 규칙을 표현할 수 있습니다. 빈 상태와 동시성, 포화 정책은 순서 규칙과 별도로 확인해야 합니다. FIFO 접수도 여러 작업자의 완료 순서를 보장하지는 않습니다.

## 꼬리 질문


<details class="cs-followup">
<summary>Q1. FIFO로 접수하면 여러 작업자의 완료 순서도 같을까요?</summary>
<div class="cs-followup-answer">
<p>작업별 실행 시간이 다르면 먼저 접수한 작업이 나중에 끝날 수 있습니다. 큐의 제거 순서와 병렬 작업의 완료 순서는 구분해야 합니다.</p>
</div>
</details>

<details class="cs-followup">
<summary>Q2. 큐를 크게 만들면 처리량도 자동으로 늘어날까요?</summary>
<div class="cs-followup-answer">
<p>처리 능력이 같다면 대기 시간과 메모리만 늘어날 수 있습니다. 최대 대기량과 거절·속도 조절 정책을 함께 정해야 합니다.</p>
</div>
</details>

---

**참고 자료**

- [Java 17 ArrayDeque](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/ArrayDeque.html)
- [Java 17 Queue](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Queue.html)

{% endraw %}
