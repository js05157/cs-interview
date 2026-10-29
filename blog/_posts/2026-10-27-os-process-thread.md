---
layout: post
title: 프로세스와 스레드
date: 2026-10-27 00:00:00 +0900
topic_id: os-process-thread
categories:
- Operating-System
tags:
- Process
description: 프로세스는 실행 중인 프로그램과 그 프로그램이 사용하는 자원을 묶어 관리하는 단위입니다. 스레드는 프로세스 안에서 코드를 실행하는
  하나의 흐름이며, 한 프로세스에 여러 스레드가 있을 수 있습니다.
permalink: /topics/os-process-thread/
github_url: https://github.com/js05157/cs-interview/blob/master/Operating-System/Process/os-process-thread.md
content_type: cs
excerpt: ''
learning_format: five-section-v1
---

{% raw %}
## 정의

**프로세스**는 실행 중인 프로그램과 그 프로그램이 사용하는 자원을 묶어 관리하는 단위입니다. **스레드**는 프로세스 안에서 코드를 실행하는 하나의 흐름이며, 한 프로세스에 여러 스레드가 있을 수 있습니다.

## 설명

같은 Java 서버 프로그램을 두 번 실행하면 보통 서로 다른 프로세스가 만들어집니다. 두 프로세스의 메모리는 기본적으로 분리되므로, 한쪽의 객체를 바꿔도 다른 쪽 객체가 함께 바뀌지는 않습니다. 데이터를 주고받으려면 소켓이나 공유 메모리 같은 별도 수단이 필요합니다.

반면 한 서버 안에서 여러 작업을 나눠 처리하려면 스레드를 사용할 수 있습니다. 어떤 작업이 응답을 기다리는 동안 다른 작업을 진행하거나, 여러 CPU 코어에서 작업을 나눠 실행할 수 있습니다.

![프로세스 A의 두 스레드는 각자 스택을 가지면서 같은 힙 객체를 참조하고, 프로세스 B는 별도의 메모리를 사용하는 그림](https://raw.githubusercontent.com/js05157/cs-interview/master/blog/assets/diagrams/process-thread.svg)

그림에서 **두 화살표가 같은 힙 객체를 가리키는 부분**을 보세요. 같은 프로세스의 스레드는 힙과 코드 등을 공유하지만, 메서드 호출과 지역 변수를 관리하는 스택은 각자 가집니다. 지역 변수에 담긴 참조가 같은 객체를 가리킬 수 있으므로, 지역 변수라고 해서 참조하는 객체까지 항상 독립적인 것은 아닙니다.

공유하면 데이터를 함께 쓰기 편하지만, 동시에 값을 바꿀 때 문제가 생길 수 있습니다. 두 스레드가 카운터의 같은 값을 읽고 각각 1을 더해 저장하면, 두 번 증가했는데 결과는 한 번만 증가한 것처럼 남을 수 있습니다. 이런 **실행 순서에 따라 결과가 달라지는 문제**를 경쟁 상태라고 합니다.

스레드가 많다고 항상 빠르지는 않습니다. CPU에서 실행할 차례를 기다리거나 같은 데이터를 바꾸려고 서로 기다릴 수 있고, 스레드마다 메모리도 필요합니다.

## 적용 예시

요청 수를 세는 상황을 단순화해 보겠습니다. Java 17에서 두 스레드가 **같은 카운터를 각각 1,000번 증가**시킵니다.

```java
import java.util.concurrent.atomic.AtomicInteger;

public class SharedCounter {
    public static void main(String[] args) throws InterruptedException {
        AtomicInteger count = new AtomicInteger();
        Runnable work = () -> {
            for (int i = 0; i < 1000; i++) count.incrementAndGet();
        };
        Thread a = new Thread(work);
        Thread b = new Thread(work);
        a.start();
        b.start();
        a.join();
        b.join();
        System.out.println(count.get()); // 2000
    }
}
```

`start()`는 새 실행 흐름을 시작하고, `join()`은 그 스레드가 끝날 때까지 기다립니다. 두 작업이 끝난 뒤 출력되는 값은 **2000**입니다.

`incrementAndGet()`은 값을 읽고 늘리는 과정을 다른 증가 연산과 겹쳐도 유실되지 않게 처리합니다. 이를 **원자적 증가**라고 합니다. 반면 공유된 일반 `int` 변수의 `count++`에는 이런 보장이 없어 동기화가 필요합니다. 이 예제는 공유 데이터의 안전한 갱신을 확인하며, 처리 속도를 비교하지는 않습니다.

## 정리

프로세스는 프로그램을 실행하는 데 필요한 자원을 담고, 스레드는 그 안에서 일을 진행합니다. 프로세스끼리는 메모리가 기본적으로 분리되지만, 같은 프로세스의 스레드는 힙 등을 공유합니다. 그래서 같은 데이터를 함께 쓰기 편하지만, 여러 스레드가 값을 바꿀 때는 동기화가 필요합니다. 스레드 수를 늘린다고 항상 빨라지는 것은 아니므로, 처리할 일과 사용할 수 있는 자원을 함께 봐야 합니다.

## 꼬리 질문


<details class="cs-followup">
<summary>Q1. 서버 프로그램을 두 번 실행했을 때, 한쪽 프로세스의 카운터를 바꾸면 다른 쪽도 바뀔까요?</summary>
<div class="cs-followup-answer">
<p>기본적으로는 바뀌지 않습니다. 각 프로세스는 별도 주소 공간과 객체를 사용하므로, 함께 바꾸려면 공유 메모리나 통신 같은 별도 연결이 필요합니다.</p>
</div>
</details>

<details class="cs-followup">
<summary>Q2. 두 스레드가 같은 카운터 값 0을 읽고 각각 1을 저장하면 왜 증가 한 번이 사라질까요?</summary>
<div class="cs-followup-answer">
<p>두 스레드 모두 이전 값 0을 기준으로 계산하기 때문입니다. 각자 1을 저장하면 최종 값도 1이 되어, 두 번의 증가 중 하나가 유실됩니다.</p>
</div>
</details>

<details class="cs-followup">
<summary>Q3. 계산이 많은 작업에서 스레드를 2개에서 20개로 늘렸는데 더 느려졌다면 무엇을 살펴봐야 할까요?</summary>
<div class="cs-followup-answer">
<p>CPU 코어에서 실행할 차례를 기다리는 시간과 실행 흐름을 바꾸는 비용을 확인합니다. 같은 데이터를 보호하는 락의 대기나 스레드별 메모리 비용도 함께 살펴봐야 합니다.</p>
</div>
</details>

---

**참고 자료**

- [OSTEP: The Abstraction — The Process](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-intro.pdf)
- [Linux man-pages: pthreads(7)](https://man7.org/linux/man-pages/man7/pthreads.7.html)
- [Java 17 Thread: start와 join](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/lang/Thread.html)
- [Java 17 AtomicInteger](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/atomic/AtomicInteger.html)
- [OpenJDK JEP 444: Virtual Threads](https://openjdk.org/jeps/444)

도식은 이 글을 위해 직접 작성했습니다. 실제 주소 배치나 물리 메모리 크기를 나타내는 그림이 아닙니다.

{% endraw %}
