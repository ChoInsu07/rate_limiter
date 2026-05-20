# Rate Limiter — Python (Token Bucket)

## 1. Project Overview

Python으로 구현한 경량 **Token Bucket** 기반 Rate Limiter입니다. 고전적인 Token Bucket 알고리즘을 사용하여 API 요청 속도를 제어하는 방법을 보여줍니다. 재사용 가능한 라이브러리, 유닛 테스트, 데모 스크립트를 포함합니다.

---

## 2. Selected Algorithm: Token Bucket

**Token Bucket** 알고리즘은 토큰을 담는 가상의 버킷을 관리합니다. 들어오는 각 요청은 토큰 하나를 소비하고, 토큰은 일정한 속도로 시간에 따라 다시 채워집니다.

### Token Refill

토큰은 설정된 속도(초당 토큰 수)로 버킷에 지속적으로 추가됩니다. 버킷이 용량에 도달하면 초과 토큰은 버려집니다.

### Token Consumption

요청이 들어오면 알고리즘은 토큰이 하나 이상 있는지 확인합니다:

- **토큰 있음** → 토큰 하나 소비 → 요청 **ALLOWED**
- **토큰 없음** → 요청 **BLOCKED**

### Burst Traffic Handling

버킷 용량 덕분에 장기 평균 refill 속도보다 더 많은 요청이 일시적으로 통과할 수 있습니다. 이는 트래픽이 짧게 폭주하는 상황에서도 정상 요청을 차단하지 않게 해줍니다.

```
Burst 예시: capacity = 5, refill = 2 tokens/sec
→ 처음 5개 요청은 즉시 통과 (burst 허용)
→ 이후 요청은 초당 ~2개로 제한
```

---

## 3. Why Token Bucket?

| 이유 | 설명 |
|---|---|
| **Burst Handling** | 짧은 트래픽 폭주를 버킷 용량으로 흡수하여 정상 요청을 차단하지 않음 |
| **Simple Implementation** | counter, timer, lock만으로 구현 가능해 유지보수가 쉬움 |
| **Practical Usage** | AWS, Stripe, GitHub API 등 실무에서 널리 사용되는 검증된 알고리즘 |

---

## 4. Architecture

```
        +-------------+
Request → RateLimiter → Allow / Block
        +-------------+
               ↓
        +-------------+
        | TokenBucket |
        | capacity=5  |
        | refill=2/s  |
        +-------------+
```

클라이언트가 `TokenBucketRateLimiter`로 요청을 보내면, limiter가 현재 토큰 수를 확인하고 refill이 필요하면 처리한 뒤 ALLOW 또는 BLOCK을 결정합니다.

---

## 5. Code Structure

```
rate_limit/
├── rate_limiter/
│   ├── __init__.py          # 패키지 export
│   └── token_bucket.py      # TokenBucketRateLimiter 구현
├── tests/
│   └── test_rate_limiter.py # 유닛 테스트
├── demo.py                  # 실행 가능한 데모 스크립트
├── requirements.txt         # 의존성
├── README.md                # 본 파일
└── .gitignore               # Python ignore 규칙
```

| 파일 | 역할 |
|---|---|
| `rate_limiter/token_bucket.py` | 핵심 구현 — thread-safe 토큰 버킷 + `allow_request()` |
| `rate_limiter/__init__.py` | `from rate_limiter import TokenBucketRateLimiter` 가능하게 함 |
| `tests/test_rate_limiter.py` | allow, block, refill 시나리오를 검증하는 unittest |
| `demo.py` | ALLOWED / BLOCKED 출력으로 실시간 동작을 보여주는 데모 |

---

## 6. How to Run

### 필수 패키지 설치

```bash
python3 -m pip install -r requirements.txt
```

### 데모 실행

```bash
python3 demo.py
```

### 테스트 실행

```bash
python3 -m unittest tests/test_rate_limiter.py -v
```

pytest 사용 시:

```bash
pytest tests/test_rate_limiter.py -v
```

---

## 7. Execution Result

```
=== Initial burst (5 tokens available) ===
Request 1: ALLOWED
Request 2: ALLOWED
Request 3: ALLOWED
Request 4: ALLOWED
Request 5: ALLOWED
Request 6: BLOCKED
Request 7: BLOCKED
Request 8: BLOCKED
Request 9: BLOCKED
Request 10: BLOCKED

=== Waiting for tokens to refill... ===
=== After refill ===
Request 11: ALLOWED
Request 12: ALLOWED
Request 13: ALLOWED
Request 14: ALLOWED
Request 15: ALLOWED
Request 16: BLOCKED
Request 17: BLOCKED
```

처음 5개 요청이 초기 버킷의 5개 토큰을 소비합니다. `refill_rate=2`로 빠르게 연속 요청이 들어오면 refill이 따라잡지 못해 6~10번은 차단됩니다. 2.5초 대기 후 약 5개의 토큰이 다시 채워져 11~15번이 통과하고 다시 소진됩니다.

---

## 8. Test Strategy

### Allow Request Test

`capacity=5`인 limiter에 5개 요청을 보냅니다. 초기 용량 내에 있으므로 5개 모두 허용되어야 합니다.

### Block Request Test

`capacity=3`인 limiter에 4개 요청을 보냅니다. 4번째 요청은 버킷이 비어있으므로 차단되어야 합니다.

### Refill Test

버킷을 소진(5개 토큰 소비)한 후 다음 요청이 차단되는지 확인하고, 0.2초 대기 후 토큰이 refill되어 새 요청이 허용되는지 검증합니다.

---

## 9. Test Result

```
test_allow_request_within_capacity ... ok
test_block_request_when_exceeded ... ok
test_refill_restores_tokens ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.205s

OK
```

3개 테스트 모두 통과합니다.

---

## 10. Future Improvements

| 개선 사항 | 설명 |
|---|---|
| **Redis 기반 분산 Limiter** | 인메모리 대신 Redis에 토큰 저장으로 여러 서버 인스턴스 지원 |
| **Sliding Window 알고리즘** | Sliding Window Log 또는 Counter로 더 부드러운 속도 제한 구현 |
| **Async 지원** | `async def allow_request()` 제공으로 asyncio 기반 웹 프레임워크 지원 |
| **FastAPI Middleware** | FastAPI 미들웨어로 패키징하여 특정 라우트 또는 전역에 적용 |
