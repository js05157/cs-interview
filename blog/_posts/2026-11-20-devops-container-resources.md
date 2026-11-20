---
layout: post
title: 컨테이너 자원과 격리
date: 2026-11-20 00:00:00 +0900
topic_id: devops-container-resources
categories:
- DevOps
tags:
- Container
description: 컨테이너 격리는 프로세스가 보는 범위와 사용할 수 있는 자원을 나누는 기능의 조합입니다. Linux namespace는 격리된
  관찰 범위를, cgroup은 자원 관리를 담당합니다.
permalink: /topics/devops-container-resources/
github_url: https://github.com/js05157/cs-interview/blob/master/DevOps/Container/devops-container-resources.md
content_type: cs
excerpt: ''
learning_format: five-section-v1
---

{% raw %}
## 정의

컨테이너 격리는 프로세스가 보는 범위와 사용할 수 있는 자원을 나누는 기능의 조합입니다. Linux namespace는 격리된 관찰 범위를, cgroup은 자원 관리를 담당합니다.

## 설명

Kubernetes의 request는 스케줄링과 자원 배분 판단에 쓰이고 limit는 런타임 제한에 연결됩니다. request를 단순한 하드 상한으로 읽지 않습니다. CPU 250m는 CPU 자원 0.25 단위이며 스레드 개수의 4분의 1이라는 뜻은 아닙니다.

CPU 제한으로 throttling이 발생하면 사용률만으로 설명하기 어려운 지연이 생길 수 있습니다. 메모리 한도 초과는 OS 차원의 종료로 나타날 수 있어 Java OutOfMemoryError나 덤프가 반드시 남지는 않습니다. JVM 힙 외에도 스택·직접 메모리·메타데이터가 예산을 사용합니다.

따라서 Xmx를 컨테이너 전체 memory limit와 같게 두는 것은 위험할 수 있습니다. 부하와 큐 대기, 종료 원인을 관찰해 여유를 정합니다. 자원 제한과 보안 격리도 별개이므로 비루트·capability·파일·네트워크 정책을 함께 검토합니다.

## 적용 예시

Pod YAML의 자원 단위와 request≤limit, 비루트 실행 설정을 검사합니다. 가상 이미지를 실제 클러스터에 배포하거나 OOM을 일으키지 않으며 예제 숫자는 운영 권장값이 아닙니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: resource-example
spec:
  containers:
    - name: app
      image: example.invalid/backend:lesson
      resources:
        requests:
          cpu: "250m"
          memory: "256Mi"
        limits:
          cpu: "1"
          memory: "512Mi"
      securityContext:
        runAsNonRoot: true
        runAsUser: 10001
        allowPrivilegeEscalation: false
```

YAML 구문과 request≤limit·비루트 설정을 정적으로 검사합니다. example.invalid 이미지는 설명용이며 apply·스케줄링·실제 cgroup·OOM은 실행하지 않습니다. 운영 리소스 권장값이 아닙니다.

## 정리

격리된 관찰 범위와 자원 사용 제한은 서로 다른 역할입니다. request와 limit, CPU와 메모리의 동작 차이를 이해해야 합니다. JVM 전체 사용량은 힙 크기보다 큽니다. 정해진 숫자를 복사하기보다 throttling·대기·종료 원인을 측정해 실제 예산을 조정해야 합니다.

## 꼬리 질문


<details class="cs-followup">
<summary>Q1. 메모리 limit와 Xmx를 같게 두면 공간을 잘 쓰는 걸까요?</summary>
<div class="cs-followup-answer">
<p>스택과 직접 메모리·메타데이터 등 힙 밖 사용량의 여유가 부족할 수 있습니다. 프로세스 전체 예산과 실측 사용량을 기준으로 정해야 합니다.</p>
</div>
</details>

<details class="cs-followup">
<summary>Q2. CPU limit가 낮으면 생성 가능한 스레드 수도 직접 줄까요?</summary>
<div class="cs-followup-answer">
<p>CPU limit는 주로 실행 시간 배분과 throttling에 영향을 줍니다. 스레드 개수의 직접 상한과는 다른 계약입니다.</p>
</div>
</details>

---

**참고 자료**

- [Kubernetes 자원 관리](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)

{% endraw %}
