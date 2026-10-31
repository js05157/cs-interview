---
layout: post
title: CPU 스케줄링
date: 2026-10-31 00:00:00 +0900
topic_id: os-cpu-scheduling
categories:
- Operating-System
tags:
- Scheduling
description: CPU 스케줄링은 실행할 준비가 된 작업 가운데 다음에 CPU를 사용할 대상을 고르는 정책입니다. 빠른 응답과 공정한 기회처럼
  원하는 목표에 따라 선택 기준이 달라집니다.
permalink: /topics/os-cpu-scheduling/
github_url: https://github.com/js05157/cs-interview/blob/master/Operating-System/Scheduling/os-cpu-scheduling.md
content_type: cs
excerpt: ''
learning_format: five-section-v1
---

{% raw %}
## 정의

CPU 스케줄링은 실행할 준비가 된 작업 가운데 다음에 CPU를 사용할 대상을 고르는 정책입니다. 빠른 응답과 공정한 기회처럼 원하는 목표에 따라 선택 기준이 달라집니다.

## 설명

디스크 응답을 기다리는 작업과 당장 실행할 수 있는 작업은 다릅니다. 운영체제는 실행 가능한 집합에서 다음 대상을 고르고, 필요하면 실행 중인 작업을 멈추는 선점을 사용합니다.

먼저 온 순서대로 처리하는 FCFS는 단순하지만 긴 작업 뒤의 짧은 작업도 기다립니다. 짧은 작업 우선은 실행 시간을 알아야 한다는 어려움이 있고, Round Robin은 시간 할당량을 나누어 돌아가며 실행합니다. 할당량이 너무 짧으면 전환 비용이 커지고 너무 길면 첫 응답이 늦어질 수 있습니다.

선택 정책과 선택된 작업으로 바꾸는 컨텍스트 스위칭을 구분하세요. 실제 Linux 정책은 커널 버전과 스케줄링 클래스에 따라 다르며, 이 세 정책으로 모두 설명되지는 않습니다.

## 적용 예시

모든 작업이 동시에 도착하고 실행 시간을 안다는 조건에서 처리 순서를 비교합니다. 아래 계산은 평균 반환 시간의 차이를 보여 주며 실제 커널의 I/O·선점 비용은 포함하지 않습니다.

```python
# 모든 작업이 시각 0에 도착하는 비선점 단일 CPU 모델
def mean_turnaround(durations):
    now = total = 0
    for duration in durations:
        now += duration
        total += now
    return total / len(durations)

fcfs = mean_turnaround([8, 2, 1])
sjf = mean_turnaround([1, 2, 8])
assert fcfs == 29 / 3
assert sjf == 5
assert sjf < fcfs
```

반환 시간은 완료 시각에서 도착 시각을 뺀 값입니다. 이 계산은 I/O, 선점, 실제 커널 오버헤드를 모델링하지 않습니다.

## 정리

CPU 스케줄링은 준비된 작업에 실행 기회를 나누는 규칙입니다. 처리 순서와 시간 할당량에 따라 응답 시간과 처리량이 달라집니다. 짧은 작업만 우선하면 다른 작업이 계속 밀리는 기아도 고려해야 합니다. 평균 완료 시간이 좋아졌다고 모든 사용자의 첫 응답까지 좋아진 것은 아닙니다.

## 꼬리 질문


<details class="cs-followup">
<summary>Q1. 짧은 작업만 계속 들어오면 긴 작업에는 어떤 문제가 생길까요?</summary>
<div class="cs-followup-answer">
<p>긴 작업이 계속 뒤로 밀려 실행 기회를 얻지 못할 수 있습니다. 이런 기아를 줄이려면 대기 시간이나 공정성을 반영하는 정책을 검토해야 합니다.</p>
</div>
</details>

<details class="cs-followup">
<summary>Q2. Round Robin의 할당량을 아주 작게 잡으면 항상 반응이 좋아질까요?</summary>
<div class="cs-followup-answer">
<p>처음 실행할 기회는 빨라질 수 있지만 전환이 너무 자주 발생합니다. 그 비용 때문에 유효한 처리량이나 전체 지연은 오히려 나빠질 수 있습니다.</p>
</div>
</details>

---

**참고 자료**

- [OSTEP: Scheduling — Introduction](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched.pdf)
- [Linux man-pages: sched(7)](https://man7.org/linux/man-pages/man7/sched.7.html)

{% endraw %}
