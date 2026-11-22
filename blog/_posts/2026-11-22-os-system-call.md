---
layout: post
title: 시스템 콜과 사용자 모드
date: 2026-11-22 00:00:00 +0900
topic_id: os-system-call
categories:
- Operating-System
tags:
- Kernel
description: 시스템 콜은 프로그램이 운영체제 커널에 파일이나 통신 같은 서비스를 요청하는 인터페이스입니다. 보호된 자원에 접근할 때 사용자
  코드와 커널 사이의 권한 경계를 지납니다.
permalink: /topics/os-system-call/
github_url: https://github.com/js05157/cs-interview/blob/master/Operating-System/Kernel/os-system-call.md
content_type: cs
excerpt: ''
learning_format: five-section-v1
---

{% raw %}
## 정의

시스템 콜은 프로그램이 운영체제 커널에 파일이나 통신 같은 서비스를 요청하는 인터페이스입니다. 보호된 자원에 접근할 때 사용자 코드와 커널 사이의 권한 경계를 지납니다.

## 설명

프로그램이나 라이브러리가 요청 인자를 준비하면 커널이 주소·권한·요청 내용을 검사하고 결과를 돌려줍니다. 권한이 바뀌었다고 반드시 다른 작업으로 실행 대상까지 바뀌는 것은 아닙니다.

Java의 파일 메서드와 OS 시스템 콜은 같은 층위가 아닙니다. 런타임과 버퍼가 중간에 있으므로 상위 메서드 한 번이 특정 시스템 콜 한 번과 일대일로 대응한다고 가정하지 않습니다.

작은 쓰기를 모으면 호출 부담을 줄일 수 있지만 지연과 손실 가능한 데이터 범위도 바뀝니다. write 성공이나 애플리케이션 버퍼의 flush가 전원 장애 뒤 영속성까지 보장하는 것은 아닙니다. 낮은 수준의 write는 일부 길이만 기록할 수 있어 반환값도 처리해야 합니다.

## 적용 예시

Java 파일 API로 내용을 쓰고 다시 읽어 결과를 확인합니다. 이 예제는 파일 내용의 왕복을 검증하며 실제 OS 호출 횟수나 저장 장치의 내구성을 측정하지 않습니다.

```java
import java.nio.file.Files;
import java.nio.file.Path;

public class FileApiDemo {
    public static void main(String[] args) throws Exception {
        Path path = Files.createTempFile("cs-system-call-", ".txt");
        try {
            Files.writeString(path, "hello");
            if (!Files.readString(path).equals("hello")) throw new AssertionError();
        } finally {
            Files.deleteIfExists(path);
        }
    }
}
```

이 예제는 Java 파일 API의 결과를 확인합니다. 한 번의 `writeString`이 정확히 한 번의 특정 시스템 콜이라는 주장을 검증하지 않습니다. 실제 호출은 OS와 JDK 구현을 추적해 확인해야 합니다.

## 정리

시스템 콜은 사용자 프로그램이 커널의 서비스를 요청하는 경로입니다. Java 메서드와 시스템 콜 사이에는 런타임과 버퍼 같은 계층이 있습니다. 권한 전환과 다른 작업으로 바뀌는 컨텍스트 스위칭도 구분해야 합니다. 파일 쓰기에서는 호출 결과뿐 아니라 필요한 내구성과 오류 처리 계약을 확인합니다.

## 꼬리 질문


<details class="cs-followup">
<summary>Q1. 파일 메서드를 한 번 호출하면 시스템 콜도 정확히 한 번일까요?</summary>
<div class="cs-followup-answer">
<p>보장되지 않습니다. 버퍼링과 JDK·OS 구현에 따라 실제 호출이 나뉘거나 합쳐질 수 있습니다.</p>
</div>
</details>

<details class="cs-followup">
<summary>Q2. write가 성공하면 정전 뒤에도 데이터가 반드시 남을까요?</summary>
<div class="cs-followup-answer">
<p>그 성공만으로 판단할 수 없습니다. 파일 시스템과 저장 장치의 동기화·내구성 계약을 별도로 확인해야 합니다.</p>
</div>
</details>

---

**참고 자료**

- [Linux man-pages: syscall(2)](https://man7.org/linux/man-pages/man2/syscall.2.html)
- [Linux man-pages: write(2)](https://man7.org/linux/man-pages/man2/write.2.html)

{% endraw %}
