# Bean 스코프와 생명주기

## 정의

Bean 스코프는 어떤 범위에서 같은 객체를 재사용할지 정하는 규칙입니다. 생명주기는 객체의 생성과 의존 주입부터 초기화·사용·정리까지의 과정입니다.

## 설명

기본 singleton은 컨테이너의 Bean 정의마다 인스턴스 하나를 재사용합니다. JVM 전체에서 유일하다는 뜻도, 동시 접근이 안전하다는 뜻도 아닙니다. 요청마다 달라지는 값을 singleton 필드에 저장하면 서로의 요청이 섞일 수 있습니다.

prototype은 컨테이너에서 새로 요청할 때 인스턴스를 생성합니다. 하지만 singleton 생성 시 한 번 주입한 prototype 참조가 호출마다 바뀌지는 않습니다. 매번 새 객체가 필요하면 ObjectProvider처럼 조회 시점을 명시하는 방법을 검토합니다.

의존 주입 뒤 초기화 콜백이 실행되고 후처리기가 객체를 감쌀 수 있습니다. 컨테이너는 관리 singleton의 종료 콜백을 호출하지만 prototype의 소멸은 일반적으로 사용자 책임입니다. 초기화 중 프록시를 거치지 않은 트랜잭션 호출이나 종료 중 무한 대기에도 주의합니다.

## 적용 예시

같은 Bean을 반복 조회하며 singleton과 prototype의 생성 횟수를 비교합니다. 컨텍스트 종료 시 어느 객체의 정리 콜백이 호출되는지도 검사합니다.

```java
package study;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.springframework.context.annotation.*;
import org.springframework.beans.factory.config.ConfigurableBeanFactory;
import static org.junit.jupiter.api.Assertions.*;
public class LifecycleTest {
  static final AtomicInteger starts=new AtomicInteger(),stops=new AtomicInteger();
  static class Resource {public void start(){starts.incrementAndGet();}public void stop(){stops.incrementAndGet();}}
  @Configuration(proxyBeanMethods=false) static class Config {
    @Bean(initMethod="start",destroyMethod="stop") Resource singleton(){return new Resource();}
    @Bean(initMethod="start",destroyMethod="stop") @Scope(ConfigurableBeanFactory.SCOPE_PROTOTYPE)
    Resource prototype(){return new Resource();}
  }
  @Test void checksOwnership(){
    starts.set(0);stops.set(0);
    try(var c=new AnnotationConfigApplicationContext(Config.class)){
      assertSame(c.getBean("singleton"),c.getBean("singleton"));
      assertNotSame(c.getBean("prototype"),c.getBean("prototype"));
      assertEquals(3,starts.get());
    }
    assertEquals(1,stops.get());
  }
}
```

`examples/spring-lab`(Java 17, Spring Boot 3.5.16)의 JUnit 예제입니다. 외부 서비스나 운영 DB 연결 없이 실행하며 문서와 실제 테스트 소스를 대조합니다. singleton·prototype 생성 횟수와 종료 콜백 관리 범위를 확인합니다.

## 정리

스코프는 재사용 범위이고 생명주기는 생성부터 정리까지의 과정입니다. 긴 수명의 객체에 짧은 수명의 의존성을 주입하면 언제 참조를 결정하는지가 중요합니다. singleton은 요청 상태를 안전하게 공유해 준다는 보장이 아닙니다. 자원의 실제 소유자와 종료 책임을 명확히 해야 합니다.

## 꼬리 질문

### Q1. singleton에 prototype을 주입하면 메서드를 부를 때마다 새 객체일까요?

생성 시 한 번 주입했다면 같은 참조를 계속 사용합니다. 매 호출에 새 인스턴스가 필요하면 컨테이너 조회 시점을 별도로 구성해야 합니다.

### Q2. prototype 연결 자원을 컨테이너 종료에 맡겨도 될까요?

컨테이너가 일반적으로 prototype 소멸까지 관리하지는 않습니다. 자원을 실제 사용하는 쪽에서 종료 책임을 정해야 합니다.

---

**참고 자료**

- [Spring Framework 6.2 공식 문서](https://docs.spring.io/spring-framework/reference/6.2/core/beans/factory-scopes.html)
- [Spring Framework 6.2 공식 문서](https://docs.spring.io/spring-framework/reference/6.2/core/beans/factory-nature.html)
