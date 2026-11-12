---
layout: post
title: 배치와 스트림 처리
date: 2026-11-12 00:00:00 +0900
topic_id: data-batch-stream
categories:
- Data-Engineering
tags:
- Pipeline
description: 배치 처리는 끝이 정해진 데이터 집합에서 결과를 계산하는 방식입니다. 스트림 처리는 계속 도착하는 데이터를 받아 상태와 결과를
  갱신하는 방식입니다.
permalink: /topics/data-batch-stream/
github_url: https://github.com/js05157/cs-interview/blob/master/Data-Engineering/Pipeline/data-batch-stream.md
content_type: cs
excerpt: ''
learning_format: five-section-v1
---

{% raw %}
## 정의

배치 처리는 끝이 정해진 데이터 집합에서 결과를 계산하는 방식입니다. 스트림 처리는 계속 도착하는 데이터를 받아 상태와 결과를 갱신하는 방식입니다.

## 설명

유한 입력은 끝에 도달했는지 알 수 있지만 무한 입력에는 시간·개수·세션 같은 윈도우와 완료 판단이 필요합니다. 작은 묶음으로 계속 처리하는 micro-batch도 구현 방식일 뿐 결과가 언제 최종인지까지 정해주지는 않습니다. 입력 범위와 키, 상태, 출력 시점을 먼저 정의합니다.

배치는 마감 시점의 정산을 재현하기 쉽고 스트림은 빠른 경보나 대시보드 갱신에 적합할 수 있습니다. 스트림도 입력 보관과 상태 초기화·출력 멱등성 정책이 있으면 재처리할 수 있습니다. 낮은 지연과 재계산 용이성을 상태·보관·운영 비용과 함께 비교합니다.

장애 복구는 입력 위치와 계산 상태, 외부 출력 효과를 일관된 지점으로 맞춰야 합니다. 중복과 순서 역전, 늦은 데이터·스키마 변경을 따로 다룹니다. 순서에 둔감한 합산도 중복은 영향을 주며 무한 입력의 중복 제거 Set은 계속 자랄 수 있어 보존 기간이 필요합니다.

## 적용 예시

유한 이벤트에서 ID 중복을 제거하고 입력 순서가 바뀌어도 합계가 같은지 검사합니다. 스트림 엔진의 체크포인트나 무한 상태·윈도우 복구를 실행하는 예제는 아닙니다.

```java
import java.util.*;
public class BatchStreamDemo {
  record Event(String id,String key,long amount){}
  static Map<String,Long> aggregate(List<Event> events){
    Map<String,Long> sums=new HashMap<>();Set<String> seen=new HashSet<>();
    for(var e:events)if(seen.add(e.id))sums.merge(e.key,e.amount,Math::addExact);
    return sums;
  }
  public static void main(String[] args){
    var a=new Event("1","shop",10);var b=new Event("2","shop",20);
    assert aggregate(List.of(a,b)).equals(Map.of("shop",30L));
    assert aggregate(List.of(b,a,a)).equals(Map.of("shop",30L));
    assert aggregate(List.of()).isEmpty();
  }
}
```

JDK 17에서 유한 입력의 이벤트 ID 중복 제거와 순서가 바뀐 합산 결과를 비교합니다. 무한 스트림·체크포인트·엔진 복구·시간 윈도우를 실행하지 않습니다. 중복 상태는 메모리 한도·보존 설계가 없는 학습 모델입니다.

## 정리

배치와 스트림은 입력의 끝과 결과 갱신 방식을 기준으로 이해할 수 있습니다. 빠른 처리와 최종 확정은 같은 의미가 아닙니다. 재처리하려면 입력 위치·상태·출력의 복구 경계를 맞춰야 합니다. 업무별로 잠정 결과와 보정, 중복 상태의 보관 범위를 정해야 합니다.

## 꼬리 질문


<details class="cs-followup">
<summary>Q1. 스트림 결과가 즉시 나오면 항상 최종 확정일까요?</summary>
<div class="cs-followup-answer">
<p>늦은 데이터와 trigger·허용 지연 정책에 따라 바뀔 수 있습니다. 잠정·확정·보정 결과의 계약을 구분해야 합니다.</p>
</div>
</details>

<details class="cs-followup">
<summary>Q2. 이벤트 ID Set을 계속 늘리면 중복 제거가 완성될까요?</summary>
<div class="cs-followup-answer">
<p>무한 입력에서는 상태도 계속 커질 수 있습니다. 중복 가능 기간과 상태 보존·재처리 정책을 함께 정해야 합니다.</p>
</div>
</details>

---

**참고 자료**

- [Flink 스트리밍 분석 기초](https://nightlies.apache.org/flink/flink-docs-stable/docs/learn-flink/streaming_analytics/)
- [Flink 시간 개념](https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/time/)

{% endraw %}
