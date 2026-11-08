---
layout: post
title: IoC와 의존성 주입
date: 2026-11-08 00:00:00 +0900
topic_id: spring-ioc-di
categories:
- Spring
tags:
- Spring-Core
description: IoC는 객체를 만들고 연결하는 제어를 컨테이너 같은 외부 주체에 맡기는 방식입니다. DI는 객체가 필요한 의존 객체를 외부에서
  전달받는 방법이며 Spring은 이를 지원하는 컨테이너를 제공합니다.
permalink: /topics/spring-ioc-di/
github_url: https://github.com/js05157/cs-interview/blob/master/Spring/Spring-Core/spring-ioc-di.md
content_type: cs
excerpt: ''
learning_format: five-section-v1
---

{% raw %}
## 정의

IoC는 객체를 만들고 연결하는 제어를 컨테이너 같은 외부 주체에 맡기는 방식입니다. DI는 객체가 필요한 의존 객체를 외부에서 전달받는 방법이며 Spring은 이를 지원하는 컨테이너를 제공합니다.

## 설명

주문 서비스가 저장소를 직접 만들면 저장 방식과 테스트 대역을 바꾸기 어렵습니다. 생성자로 저장소 인터페이스를 받으면 서비스는 계약에 집중하고, 실제 구현의 선택과 연결은 설정에서 담당할 수 있습니다.

Spring 컨테이너는 Bean 정의를 읽어 객체를 생성하고 의존성을 연결한 뒤 초기화와 후처리를 적용합니다. 같은 타입의 후보가 여러 개면 Qualifier나 Primary 등으로 선택을 분명히 해야 합니다. 일반적으로 new로 만든 객체에는 이 관리 과정이 자동 적용되지 않습니다.

생성자 주입은 필수 의존성을 드러내고 컨테이너 없는 테스트도 쉽게 합니다. A와 B가 서로의 완성된 객체를 요구하는 순환은 setter로 우회하기 전에 책임을 나누거나 중재 서비스를 둘지 검토합니다. DI를 사용한다는 사실만으로 좋은 추상화가 생기지는 않습니다.

## 적용 예시

인터페이스에 의존하는 서비스를 컨테이너가 생성하고, 등록한 동일 의존 Bean을 연결하는지 검사합니다. 생성자 연결이 실제로 성립하는지 확인하는 작은 컨텍스트 테스트입니다.

```java
package study;
import org.junit.jupiter.api.Test;
import org.springframework.context.annotation.*;
import static org.junit.jupiter.api.Assertions.*;
public class IocTest {
  interface Rate { int price(); }
  record FixedRate(int price) implements Rate {}
  record Checkout(Rate rate) { int total(int n){return rate.price()*n;} }
  @Configuration(proxyBeanMethods=false) static class Config {
    @Bean Rate rate(){return new FixedRate(100);}
    @Bean Checkout checkout(Rate rate){return new Checkout(rate);}
  }
  @Test void injectsConstructor(){
    try(var ctx=new AnnotationConfigApplicationContext(Config.class)){
      assertEquals(300,ctx.getBean(Checkout.class).total(3));
      assertSame(ctx.getBean(Rate.class),ctx.getBean(Checkout.class).rate());
    }
  }
}
```

`examples/spring-lab`(Java 17, Spring Boot 3.5.16)의 JUnit 예제입니다. 외부 서비스나 운영 DB 연결 없이 실행하며 문서와 실제 테스트 소스를 대조합니다. 생성자 의존성과 컨테이너의 동일 Bean 연결을 확인합니다.

## 정리

IoC는 객체 제어를 외부로 옮기는 개념이고 DI는 의존 객체를 전달하는 방법입니다. 서비스가 필요한 계약을 생성자로 드러내면 구현 선택과 업무 로직을 분리할 수 있습니다. Spring의 관리는 실제 Bean 등록 경계 안에서 적용됩니다. 순환 의존이나 불필요한 결합은 주입 방식보다 책임 설계를 먼저 돌아봐야 합니다.

## 꼬리 질문


<details class="cs-followup">
<summary>Q1. 클래스에 애노테이션만 붙이면 직접 new한 객체도 주입받을까요?</summary>
<div class="cs-followup-answer">
<p>일반적인 직접 생성 객체는 컨테이너의 생성·주입·후처리 과정을 거치지 않습니다. 애노테이션뿐 아니라 실제 Bean 등록과 생성 경계를 확인해야 합니다.</p>
</div>
</details>

<details class="cs-followup">
<summary>Q2. 생성자 주입을 쓰면 컨테이너 없이도 서비스를 테스트할 수 있을까요?</summary>
<div class="cs-followup-answer">
<p>생성자에 테스트 대역을 전달해 순수하게 생성할 수 있습니다. 다만 프록시나 트랜잭션 같은 컨테이너 기능은 별도의 통합 검사 대상입니다.</p>
</div>
</details>

---

**참고 자료**

- [Spring Framework 6.2 공식 문서](https://docs.spring.io/spring-framework/reference/6.2/core/beans/dependencies/factory-collaborators.html)

{% endraw %}
