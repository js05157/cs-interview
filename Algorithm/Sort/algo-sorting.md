# 정렬과 안정성

## 정의

정렬은 비교 기준에 따라 원소 순서를 재배치하는 작업입니다. 안정 정렬은 비교 결과가 같은 원소들의 기존 상대 순서를 유지합니다.

## 설명

병합 정렬은 나눈 부분을 정렬한 뒤 두 정렬열을 합칩니다. 동점에서 원래 앞쪽 원소를 먼저 고르면 안정성을 유지할 수 있습니다. 퀵 정렬은 피벗 기준으로 나누며 일반적인 단순 구현은 안정적이지 않고 입력에 따라 최악 제곱 시간이 될 수 있습니다.

안정성·제자리 여부·최악 시간·추가 공간은 다른 성질입니다. 일반 비교 정렬의 최악 비교 하한 Ω(n log n)은 값 범위나 자릿수 조건을 활용하는 계수·기수 정렬에 그대로 적용하지 않습니다.

Java 객체 배열의 Arrays.sort는 안정성을 보장하지만 모든 타입과 버전의 구현을 같다고 보면 안 됩니다. Comparator는 추이성 등 일관된 순서를 지켜야 하며 안정 정렬도 원래 입력이 불규칙하면 결과의 전체 결정성을 만들지는 못합니다.

## 적용 예시

같은 점수의 객체가 기존 순서를 유지하는지와 원시 배열의 정렬 결과를 확인합니다. 여러 기준이 필요하면 thenComparing으로 명시하고 DB 조회에는 고유 보조 정렬 키도 검토합니다.

```java
import java.util.*;
public class StableSortDemo {
  record Row(int score,String name){}
  public static void main(String[] args){
    Row[] rows={new Row(2,"a"),new Row(1,"b"),new Row(2,"c"),new Row(1,"d")};
    Arrays.sort(rows,Comparator.comparingInt(Row::score));
    assert Arrays.stream(rows).map(Row::name).toList().equals(List.of("b","d","a","c"));
    int[] values={3,-1,3,0};Arrays.sort(values);
    assert Arrays.equals(values,new int[]{-1,0,3,3});
  }
}
```

JDK 17에서 객체 동점 순서 보존과 원시 배열 정렬을 확인합니다. 특정 정렬 구현의 비교 횟수·메모리 사용량은 측정하지 않습니다.

## 정리

정렬의 정확성은 일관된 비교 기준에서 시작합니다. 안정성은 동점 원소의 기존 순서를 보존하는 성질이며 속도나 공간과는 구분해야 합니다. 안정 정렬이라고 불규칙한 입력까지 언제나 같은 최종 순서가 되는 것은 아닙니다. 요구하는 동점 처리와 API의 보장을 명시적으로 선택해야 합니다.

## 꼬리 질문

### Q1. 안정 정렬이면 DB 동점 행의 페이지 순서도 항상 같을까요?

원래 입력 순서가 달라지면 안정 정렬만으로 결정되지 않습니다. 고유 보조 키 등으로 필요한 전체 순서를 명시해야 합니다.

### Q2. a보다 b가 크고 b보다 c가 큰데 c보다 a가 크다고 비교하면 어떤 문제가 생길까요?

일관된 순서를 만들 수 없어 비교 계약을 깨뜨립니다. 정렬 전에 Comparator의 추이성과 동점 기준을 확인해야 합니다.

---

**참고 자료**

- [Java 17 Arrays](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Arrays.html)
- [MIT 6.006 강의 3](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/resources/mit6_006f11_lec03/)
