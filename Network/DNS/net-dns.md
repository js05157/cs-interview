# DNS 조회와 캐싱

## 정의

DNS는 도메인 이름에 연결된 정보를 여러 서버가 나누어 관리하고 조회하는 시스템입니다. 서비스 이름으로 IP 주소를 찾는 일이 대표적이며, 캐시를 이용해 같은 조회를 반복하는 비용을 줄입니다.

## 설명

이름을 물으면 먼저 OS·런타임이나 재귀 리졸버의 캐시가 사용될 수 있습니다. 필요한 정보가 없으면 리졸버가 위임 관계를 따라 권한 서버의 답을 구하고, TTL에 맞춰 보관합니다. 이미 아는 답과 위임이 있으므로 매번 루트부터 모두 조회하지는 않습니다.

권한 서버는 담당 영역의 정보를 응답하고, 재귀 리졸버는 클라이언트 대신 답을 찾아 캐싱합니다. 존재하지 않는 이름이라는 응답도 정해진 규칙으로 캐시될 수 있습니다. NXDOMAIN과 응답을 못 받은 타임아웃은 구분해야 합니다.

주소를 바꿔도 기존 캐시는 이전 TTL까지 남을 수 있고 이미 열린 연결도 유지될 수 있습니다. DNS는 UDP만 사용하는 기술도 아닙니다.

## 적용 예시

기존 Java 예제로 localhost 이름 해석 결과를 확인합니다. 이는 hosts나 OS 설정으로 해결될 수도 있어 외부 DNS 캐시나 장애 전환 시험은 아닙니다.

```java
import java.net.InetAddress;

public class NameResolutionDemo {
    public static void main(String[] args) throws Exception {
        InetAddress[] addresses = InetAddress.getAllByName("localhost");
        if (addresses.length == 0) throw new AssertionError("no address");
        for (InetAddress address : addresses) {
            if (!address.isLoopbackAddress()) throw new AssertionError(address);
        }
    }
}
```

일반적인 localhost 설정에서 JVM의 이름 해석 결과를 확인합니다. hosts나 OS 설정으로 해결될 수 있으므로 외부 DNS의 반복 조회·TTL·장애 전환을 검증하는 코드는 아닙니다. 사용자 정의 localhost 설정이 있다면 결과가 달라질 수 있습니다.

## 정리

DNS는 이름에 대한 정보를 분산해서 조회하고 재사용합니다. 권한 서버의 원본 응답과 리졸버·애플리케이션 캐시는 서로 다른 위치입니다. 레코드 변경이 모든 사용자에게 즉시 같은 결과를 만들지는 않습니다. 주소 조회 결과와 기존 연결의 수명도 따로 확인해야 합니다.

## 꼬리 질문

### Q1. TTL을 0으로 바꾸면 예전 주소를 받은 캐시도 즉시 사라질까요?

이미 저장된 응답은 이전 TTL의 영향을 받을 수 있습니다. 변경 전에 기존 캐시 수명을 고려해야 합니다.

### Q2. DNS가 새 IP를 반환하는데도 기존 서버로 요청이 갈 수 있을까요?

이미 열린 연결이 재사용되면 가능합니다. JVM·OS 캐시뿐 아니라 연결 풀의 수명도 확인해야 합니다.

---

**참고 자료**

- [RFC 1034: DNS Concepts and Facilities](https://www.rfc-editor.org/rfc/rfc1034.html)
- [RFC 1035: DNS Implementation and Specification](https://www.rfc-editor.org/rfc/rfc1035.html)
- [RFC 2308: Negative Caching](https://www.rfc-editor.org/rfc/rfc2308.html)
- [RFC 7766: DNS Transport over TCP](https://www.rfc-editor.org/rfc/rfc7766.html)
