# Docker 이미지와 컨테이너

## 정의

Docker 이미지는 프로그램과 실행에 필요한 파일을 담는 배포 산출물입니다. 컨테이너는 이미지에서 시작한 격리된 프로세스이며 이미지와 실행 인스턴스는 구분합니다.

## 설명

이미지의 읽기 전용 계층 위에 컨테이너의 쓰기 계층을 사용합니다. 컨테이너를 지우는 것과 volume 데이터를 지우는 것은 별도 정책입니다. DB나 업로드 파일은 쓰기 계층에만 맡기지 말고 외부 저장과 백업·복구를 설계합니다.

멀티 스테이지 빌드는 컴파일 도구와 실행 환경을 나눠 필요한 산출물만 복사합니다. 빌드 문맥에 비밀이 들어가면 이 방식만으로 안전해지지는 않습니다. COPY·ENV·ARG·로그와 빌드용 secret의 노출 경로를 검토합니다.

Linux 컨테이너는 호스트 커널을 공유하며 Desktop의 중간 Linux VM과 각 컨테이너를 구분합니다. 비루트 실행도 모든 권한 문제를 해결하지는 않습니다. 태그는 다른 이미지로 바뀔 수 있어 검토한 digest와 업데이트 정책을 관리하고 이미지 크기를 취약점 부재로 해석하지 않습니다.

## 적용 예시

Hello.java를 빌드 단계에서 컴파일하고 Hello.class만 실행 단계로 복사합니다. 네트워크와 쓰기 권한을 제한한 실행에서 출력과 Java 버전을 확인하되 장기 HTTP 서버의 신호·drain까지 검증하는 예제는 아닙니다.

```java
public class Hello {
  public static void main(String[] args){
    assert System.getProperty("java.version").startsWith("17");
    System.out.println("container demo");
  }
}
```

같은 디렉터리에 Hello.java를 두는 학습용 Dockerfile입니다.

```dockerfile
FROM eclipse-temurin:17-jdk AS build
WORKDIR /build
COPY Hello.java .
RUN javac -encoding UTF-8 Hello.java
FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=build /build/Hello.class /app/
USER 10001:10001
ENTRYPOINT ["java", "-ea", "-cp", "/app", "Hello"]
```

Hello의 Java 코드는 JDK 17에서 실행합니다. 문서의 Java·Dockerfile 그대로 실제 멀티 스테이지 빌드 후 UID/GID 10001:10001, 네트워크 없음·읽기 전용 루트 파일 시스템으로 실행해 `container demo` 출력과 Java 17 assertion을 확인했습니다. 사용한 베이스 digest는 검증 보고서에 기록했습니다. 취약점 스캔·HTTP 서버 신호 처리를 검증한 것은 아니며 실제 운영은 검토한 digest·업데이트 정책을 따로 정합니다.

## 정리

이미지는 실행 파일을 담은 산출물이고 컨테이너는 그것으로 시작한 프로세스입니다. 빌드와 실행의 분리는 불필요한 도구를 줄일 수 있지만 비밀이나 취약점을 자동 제거하지는 않습니다. 영속 데이터와 권한·자원·종료 정책을 별도로 정해야 합니다. 검토한 이미지 식별자와 실제 실행 조건을 함께 기록하는 것이 중요합니다.

## 꼬리 질문

### Q1. 컨테이너가 삭제돼도 쓰기 계층의 업로드가 남을까요?

그 계층에만 저장했다면 컨테이너 삭제로 잃을 수 있습니다. 영속 저장소와 백업·복구 정책을 별도로 마련해야 합니다.

### Q2. 작은 이미지와 비루트 USER면 보안 검사는 끝날까요?

크기는 취약점 부재를 뜻하지 않고 비루트도 모든 권한을 제거하지 않습니다. 의존성·capability·마운트·네트워크 등 실제 실행 조건을 확인해야 합니다.

---

**참고 자료**

- [Docker 이미지 개념](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-an-image/)
- [Docker 멀티 스테이지](https://docs.docker.com/build/building/multi-stage/)
