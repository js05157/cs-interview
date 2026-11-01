---
layout: post
title: 뮤텍스와 세마포어
date: 2026-11-01 00:00:00 +0900
topic_id: os-synchronization
categories:
- Operating-System
tags:
- Concurrency
description: 뮤텍스는 공유 데이터를 한 번에 하나의 실행 흐름만 다루도록 보호하는 락입니다. 세마포어는 허가 개수를 정해 동시에 접근할
  수 있는 실행 수를 제한합니다.
permalink: /topics/os-synchronization/
github_url: https://github.com/js05157/cs-interview/blob/master/Operating-System/Concurrency/os-synchronization.md
content_type: cs
excerpt: ''
learning_format: five-section-v1
---

{% raw %}
## 정의

뮤텍스는 공유 데이터를 한 번에 하나의 실행 흐름만 다루도록 보호하는 락입니다. 세마포어는 허가 개수를 정해 동시에 접근할 수 있는 실행 수를 제한합니다.

## 설명

공유 카운터의 증가처럼 읽기와 쓰기를 묶어야 하는 구간을 임계 구역이라고 합니다. 뮤텍스를 얻은 실행 흐름만 그 구간을 지나고, 나갈 때 해제하여 다른 실행이 진행하게 합니다.

세마포어는 외부 API 호출을 동시에 세 개까지만 허용하는 식으로 쓸 수 있습니다. Java Semaphore는 누가 획득했는지 소유권을 강제하지 않으므로, 허가 하나짜리를 뮤텍스와 완전히 같은 계약이라고 생각하면 안 됩니다.

동시 실행 수 제한은 초당 요청 수 제한과도 다릅니다. 락을 잡은 채 느린 I/O를 오래 수행하거나 여러 락을 다른 순서로 얻으면 대기와 교착 위험이 커집니다. volatile의 가시성만으로 count++ 전체가 원자적으로 되지는 않습니다.

## 적용 예시

제한된 자원의 허가를 얻고 작업한 뒤 반환하는 Java 예제입니다. 획득 성공 여부를 확인하고 finally에서 정확히 한 번 반환하는 흐름을 보세요.

```java
import java.util.concurrent.Semaphore;

public class SemaphoreDemo {
    public static void main(String[] args) throws InterruptedException {
        Semaphore permits = new Semaphore(1);
        permits.acquire();
        try {
            if (permits.tryAcquire()) throw new AssertionError("over capacity");
        } finally {
            permits.release();
        }
        if (permits.availablePermits() != 1) throw new AssertionError("leak");
    }
}
```

획득에 성공한 경우에만 `finally`에서 정확히 한 번 반환합니다. 실패한 획득 뒤에도 무조건 반환하면 허가 수가 잘못 증가할 수 있습니다.

## 정리

뮤텍스는 공유 상태를 함께 바꾸는 구간을 보호합니다. 세마포어는 여러 실행이 사용할 자원의 동시 접근 수를 조절합니다. 둘은 목적과 소유권 계약이 같지 않으므로 보호할 데이터와 허용 수를 먼저 정해야 합니다. 획득 실패나 예외가 나더라도 허가와 락의 균형을 유지하는 것이 중요합니다.

## 꼬리 질문


<details class="cs-followup">
<summary>Q1. 허가 획득에 실패했는데도 release를 호출하면 어떻게 될까요?</summary>
<div class="cs-followup-answer">
<p>실제로 얻지 않은 허가를 돌려주어 허용 수가 늘어날 수 있습니다. 획득에 성공한 경로에서만 정확히 한 번 반환해야 합니다.</p>
</div>
</details>

<details class="cs-followup">
<summary>Q2. 세마포어로 동시 호출을 세 개로 제한하면 초당 세 번만 호출될까요?</summary>
<div class="cs-followup-answer">
<p>아닙니다. 각 호출이 빨리 끝나면 같은 허가를 여러 번 재사용하므로 초당 호출 수는 세 번보다 많을 수 있습니다.</p>
</div>
</details>

---

**참고 자료**

- [OSTEP: Locks](https://pages.cs.wisc.edu/~remzi/OSTEP/threads-locks.pdf)
- [Linux man-pages: futex(2)](https://man7.org/linux/man-pages/man2/futex.2.html)
- [Java 17 Semaphore API](https://docs.oracle.com/en/java/javase/17/docs/api/java/util/concurrent/Semaphore.html)

{% endraw %}
