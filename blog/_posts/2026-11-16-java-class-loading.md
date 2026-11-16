---
layout: post
title: 클래스 로딩과 초기화
date: 2026-11-16 00:00:00 +0900
topic_id: java-class-loading
categories:
- Java
tags:
- JVM
description: 클래스의 생명주기는 로딩·링크·초기화로 구분합니다. 클래스를 읽어 사용할 수 있게 하는 것과 static 초기화 코드를 실행하는
  것은 같은 시점이 아닐 수 있습니다.
permalink: /topics/java-class-loading/
github_url: https://github.com/js05157/cs-interview/blob/master/Java/JVM/java-class-loading.md
content_type: cs
excerpt: ''
learning_format: five-section-v1
---

{% raw %}
## 정의

클래스의 생명주기는 로딩·링크·초기화로 구분합니다. 클래스를 읽어 사용할 수 있게 하는 것과 static 초기화 코드를 실행하는 것은 같은 시점이 아닐 수 있습니다.

## 설명

로딩 뒤 링크에서는 검증·준비·해석을 수행하며 해석 일부는 늦게 일어날 수 있습니다. 초기화에서는 static 초기화식과 블록을 실행하고 스레드 사이의 동기화 규칙도 적용합니다.

인스턴스 생성이나 특정 static 멤버의 능동 사용은 초기화를 유발할 수 있습니다. 반면 클래스 리터럴이나 컴파일 타임 상수 접근이 언제나 초기화를 유발하지는 않습니다. static final이라도 메서드 결과로 값을 정한다면 컴파일 타임 상수와 다릅니다.

타입의 정체성에는 클래스 이름뿐 아니라 정의한 로더도 포함됩니다. 같은 이름의 캐스팅 오류는 로더와 중복 의존성을 확인하고, static 외부 I/O나 실패한 초기화를 단순 메서드 재호출처럼 복구한다고 가정하지 않습니다.

## 적용 예시

Class.forName의 initialize=false 조회와 static 필드의 반사 접근을 비교합니다. 초기화가 한 번 실행되는 흐름을 확인하며 다중 로더 충돌이나 언로딩을 직접 시험하지는 않습니다.

```java
public class ClassLoadingDemo {
  static int initialized;
  public static class Lazy {
    public static final int VALUE=init();
    static int init(){initialized++;return 7;}
  }
  public static void main(String[] args)throws Exception{
    Class<?> c=Class.forName("ClassLoadingDemo$Lazy",false,ClassLoadingDemo.class.getClassLoader());
    assert initialized==0;
    assert ((Integer)c.getField("VALUE").get(null))==7;
    assert initialized==1;
    Class.forName("ClassLoadingDemo$Lazy",true,c.getClassLoader());
    assert initialized==1;
  }
}
```

JDK 17에서 초기화하지 않는 조회와 static 필드의 반사 접근에 의한 초기화, 한 번 실행을 확인합니다. 다중 로더 충돌이나 언로딩은 테스트하지 않습니다.

## 정리

로딩과 초기화는 클래스 생명주기의 다른 단계입니다. 어떤 사용이 초기화를 유발하는지 알아야 시작 시점의 실행을 설명할 수 있습니다. 같은 이름이라도 정의한 로더가 다르면 다른 타입일 수 있습니다. 초기화의 실패와 로더 생존 참조도 운영 수명 주기에서 관리해야 합니다.

## 꼬리 질문


<details class="cs-followup">
<summary>Q1. 클래스 리터럴을 읽었다고 static 초기화가 반드시 실행됐을까요?</summary>
<div class="cs-followup-answer">
<p>그 자체만으로는 반드시 그렇지 않습니다. 실제 능동 사용과 초기화 규칙을 확인해야 합니다.</p>
</div>
</details>

<details class="cs-followup">
<summary>Q2. 클래스 이름이 같은데 캐스팅이 실패하면 무엇을 더 확인할까요?</summary>
<div class="cs-followup-answer">
<p>서로 다른 정의 로더가 같은 이름을 별도 타입으로 만들었을 수 있습니다. 로더 정보와 의존성 중복을 함께 확인합니다.</p>
</div>
</details>

---

**참고 자료**

- [JLS 17 실행·초기화](https://docs.oracle.com/javase/specs/jls/se17/html/jls-12.html)
- [JVMS 17 런타임 영역](https://docs.oracle.com/javase/specs/jvms/se17/html/jvms-2.html)

{% endraw %}
