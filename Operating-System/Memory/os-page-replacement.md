# 페이지 교체와 스래싱

## 정의

페이지 교체는 메모리가 부족할 때 어떤 페이지를 회수할지 고르는 정책입니다. 필요한 페이지를 자꾸 내보냈다가 다시 가져오느라 유용한 처리가 줄어드는 상태를 스래싱이라고 합니다.

## 설명

프로그램이 자주 쓰는 페이지 집합을 RAM에 충분히 유지하지 못하면 회수와 재접근이 반복될 수 있습니다. 깨끗한 파일 페이지는 다시 읽을 수 있어 버릴 수 있지만 변경된 페이지는 별도 기록이 필요할 수 있습니다.

FIFO는 들어온 순서, LRU는 마지막 사용 시점을 기준으로 대상을 고르는 교육용 정책입니다. Clock은 참조 정보를 사용해 비용을 낮추는 근사 방식이며 실제 커널을 정확한 LRU 하나로 설명할 수는 없습니다.

폴트가 많아도 첫 접근처럼 정상적인 원인이 있습니다. 스래싱을 판단하려면 반복 입출력과 실제 처리량을 함께 봐야 합니다. 동시에 실행할 작업 수나 한 작업이 쓰는 메모리를 줄이는 방법도 필요합니다.

## 적용 예시

정해진 참조열을 제한된 프레임 수에 넣어 LRU 정책의 동작을 계산합니다. 같은 페이지를 다시 찾을 때 이미 회수되었다면 미스가 늘어나는 흐름을 확인합니다.

```python
from collections import OrderedDict

def lru_faults(sequence, capacity):
    cache = OrderedDict()
    faults = 0
    for page in sequence:
        if page not in cache:
            faults += 1
            if len(cache) == capacity:
                cache.popitem(last=False)
        cache[page] = True
        cache.move_to_end(page)
    return faults

assert lru_faults([1, 2, 1, 3, 1, 2], 2) == 4
assert lru_faults([1, 2, 1, 3, 1, 2], 3) == 3
```

이는 참조열에 대한 LRU 계산 모형입니다. 실제 페이지 폴트 횟수나 디스크 I/O 시간을 측정하는 코드는 아닙니다.

## 정리

페이지 교체는 한정된 RAM에서 남길 페이지를 선택하는 일입니다. 필요한 작업 집합을 유지하지 못하면 반복적인 이동 때문에 스래싱이 생길 수 있습니다. 단순 폴트 수나 스왑 사용량만으로 성능 문제를 결론 내리면 안 됩니다. 동시 작업 수와 접근 지역성, 실제 처리량을 함께 살펴야 합니다.

## 꼬리 질문

### Q1. 페이지 폴트가 많으면 항상 스래싱일까요?

첫 접근이나 정상적인 매핑 준비에서도 폴트가 날 수 있습니다. 반복적인 회수·복원으로 유효 처리량이 떨어지는지 확인해야 합니다.

### Q2. 배치를 더 많이 병렬 실행했더니 느려지는 이유가 메모리일 수도 있을까요?

동시 작업들의 필요한 페이지 집합이 RAM을 넘으면 그럴 수 있습니다. 배치 동시성을 낮추거나 작업 집합을 줄여 입출력과 처리량 변화를 비교합니다.

---

**참고 자료**

- [OSTEP: Beyond Physical Memory — Policies](https://pages.cs.wisc.edu/~remzi/OSTEP/vm-beyondphys-policy.pdf)
- [Linux man-pages: proc_meminfo(5)](https://man7.org/linux/man-pages/man5/proc_meminfo.5.html)
