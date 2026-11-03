---
layout: post
title: 가상 메모리
date: 2026-11-03 00:00:00 +0900
topic_id: os-virtual-memory
categories:
- Operating-System
tags:
- Memory
description: 가상 메모리는 프로그램이 사용하는 주소와 실제 RAM의 위치를 분리하는 방식입니다. 프로세스마다 자신만의 주소 공간을 사용하도록
  하여 메모리 배치와 보호를 관리합니다.
permalink: /topics/os-virtual-memory/
github_url: https://github.com/js05157/cs-interview/blob/master/Operating-System/Memory/os-virtual-memory.md
content_type: cs
excerpt: ''
learning_format: five-section-v1
---

{% raw %}
## 정의

가상 메모리는 프로그램이 사용하는 주소와 실제 RAM의 위치를 분리하는 방식입니다. 프로세스마다 자신만의 주소 공간을 사용하도록 하여 메모리 배치와 보호를 관리합니다.

## 설명

프로그램이 가상 주소로 접근하면 하드웨어와 운영체제의 매핑 정보를 통해 물리 주소를 찾습니다. 같은 숫자의 주소라도 프로세스별 매핑이 다르면 서로 다른 데이터를 가리킬 수 있습니다. 명시적인 공유 매핑은 같은 물리 페이지를 연결할 수도 있습니다.

필요한 매핑이 아직 준비되지 않았거나 권한 문제가 있으면 페이지 폴트 처리가 필요합니다. 새 메모리를 준비하거나 이미 RAM에 있는 페이지를 연결할 수도 있으므로, 모든 폴트가 디스크 읽기는 아닙니다.

가상 주소 공간의 크기는 현재 사용 중인 RAM 크기와 같지 않습니다. 스왑이 없는 시스템도 가상 메모리를 쓰며, JVM 힙 외에 스택·네이티브 버퍼 등도 실제 메모리 예산에 포함해야 합니다.

## 적용 예시

두 프로세스가 같은 가상 페이지 번호를 서로 다른 프레임에 연결하는 계산 예제입니다. 결과를 비교해 주소의 숫자만으로 같은 메모리라고 판단할 수 없는 이유를 확인합니다.

```python
# 주소 공간별 매핑을 설명하는 모형. 실제 MMU 구현은 아닙니다.
page_size = 4096
virtual_address = 4096 + 17
vpn, offset = divmod(virtual_address, page_size)
process_a = {1: 8}
process_b = {1: 20}
physical_a = process_a[vpn] * page_size + offset
physical_b = process_b[vpn] * page_size + offset
assert physical_a == 32785
assert physical_b == 81937
assert physical_a != physical_b
```

같은 가상 페이지 번호를 다른 프레임으로 매핑하는 원리를 보여줍니다. 페이지 크기 4096은 예제의 가정이며 모든 환경의 고정값이 아닙니다.

## 정리

가상 메모리는 프로그램의 주소를 물리 메모리 배치와 분리합니다. 프로세스별 매핑으로 격리와 보호를 제공하면서 필요한 공유도 구성할 수 있습니다. 가상 공간의 크기와 실제 상주 RAM, 스왑은 서로 다른 지표입니다. 메모리 문제를 볼 때는 주소 크기만이 아니라 실제 사용량과 접근·회수 상태를 살펴야 합니다.

## 꼬리 질문


<details class="cs-followup">
<summary>Q1. 두 프로세스가 같은 가상 주소를 쓰면 같은 데이터일까요?</summary>
<div class="cs-followup-answer">
<p>반드시 그렇지는 않습니다. 프로세스별 매핑이 다른 물리 페이지를 가리킬 수 있으며, 명시적으로 공유한 경우와 구분해야 합니다.</p>
</div>
</details>

<details class="cs-followup">
<summary>Q2. 스왑을 끄면 가상 메모리를 쓰지 않는 걸까요?</summary>
<div class="cs-followup-answer">
<p>아닙니다. 주소 변환과 접근 보호 같은 기능은 스왑이 없어도 사용합니다.</p>
</div>
</details>

---

**참고 자료**

- [OSTEP: The Abstraction — Address Spaces](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-intro.pdf)
- [Linux man-pages: mmap(2)](https://man7.org/linux/man-pages/man2/mmap.2.html)

{% endraw %}
