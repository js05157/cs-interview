---
layout: post
title: 컨텍스트 스위칭
date: 2026-10-30 00:00:00 +0900
topic_id: os-context-switch
categories:
- Operating-System
tags:
- Process
description: 컨텍스트 스위칭은 CPU가 실행할 작업을 바꾸면서 이전 상태를 저장하고 다음 상태를 복원하는 과정입니다. 멈춘 작업을 나중에
  이어서 실행하려면 필요합니다.
permalink: /topics/os-context-switch/
github_url: https://github.com/js05157/cs-interview/blob/master/Operating-System/Process/os-context-switch.md
content_type: cs
excerpt: ''
learning_format: five-section-v1
---

{% raw %}
## 정의

컨텍스트 스위칭은 CPU가 실행할 작업을 바꾸면서 이전 상태를 저장하고 다음 상태를 복원하는 과정입니다. 멈춘 작업을 나중에 이어서 실행하려면 필요합니다.

## 설명

한 코어도 여러 작업을 번갈아 진행할 수 있습니다. I/O를 기다리거나 실행 시간을 나눌 때, 운영체제는 현재 실행 위치와 레지스터 같은 정보를 남기고 다음 작업의 상태를 불러옵니다.

그림의 저장 → 선택 → 복원 순서를 따라가 보세요. 스케줄러가 누구를 실행할지 고르는 정책과 실제 상태를 바꾸는 전환은 서로 다른 역할입니다. 커널에 들어갔다 같은 작업으로 돌아올 수도 있으므로 모드 전환이 항상 컨텍스트 스위칭인 것은 아닙니다.

전환에는 시간뿐 아니라 CPU 캐시의 지역성이 약해지는 비용도 생길 수 있습니다. 같은 프로세스의 스레드는 주소 공간을 공유하지만 실제 비용은 하드웨어와 실행 상황에 따라 달라집니다.

![태스크 A의 상태 저장, 다음 태스크 선택, 태스크 B의 상태 복원과 실행 재개 흐름](https://raw.githubusercontent.com/js05157/cs-interview/master/blog/assets/diagrams/os-context-switch.svg?v=b05f9330693a)

## 적용 예시

스레드 풀을 늘렸는데 응답이 느려졌다면 실행 대기열·전환 횟수·락 대기를 함께 봅니다. Linux getrusage의 자발적/비자발적 전환 카운터는 원인을 좁히는 단서이며, I/O를 기다리며 양보한 전환이 많다는 사실만으로 장애라고 판단하지 않습니다. sleep의 경과 시간도 대기와 재실행 지연을 포함하므로 전환 명령 자체의 비용으로 사용하지 않습니다.

## 정리

컨텍스트 스위칭은 멈춘 실행을 다시 이어 가도록 상태를 바꾸는 과정입니다. 여러 작업이 CPU를 나누어 쓰게 하지만 전환 자체에도 비용이 듭니다. 모드 전환 횟수와 다른 작업으로 바뀐 횟수는 같지 않습니다. 전환 수만 줄이기보다 필요한 동시성과 실제 지연을 함께 봐야 합니다.

## 꼬리 질문


<details class="cs-followup">
<summary>Q1. 시스템 콜이 끝난 뒤 같은 작업으로 돌아오면 컨텍스트 스위칭일까요?</summary>
<div class="cs-followup-answer">
<p>반드시 그렇지는 않습니다. 커널 권한으로 바뀌는 것과 CPU의 실행 대상이 다른 작업으로 바뀌는 것은 구분해야 합니다.</p>
</div>
</details>

<details class="cs-followup">
<summary>Q2. 전환 횟수가 높은 서버에서 스레드를 무조건 줄여도 될까요?</summary>
<div class="cs-followup-answer">
<p>먼저 CPU 경쟁인지 정상적인 I/O 대기인지 확인해야 합니다. 필요한 동시성까지 줄이면 처리량이나 응답성이 나빠질 수 있습니다.</p>
</div>
</details>

---

**참고 자료**

- [OSTEP: Limited Direct Execution](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-mechanisms.pdf)
- [Linux man-pages: getrusage(2)](https://man7.org/linux/man-pages/man2/getrusage.2.html)

{% endraw %}
