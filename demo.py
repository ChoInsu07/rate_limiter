import time

from rate_limiter import TokenBucketRateLimiter


def main():
    limiter = TokenBucketRateLimiter(capacity=5, refill_rate=2, refill_interval=1.0)

    print("=== Initial burst (5 tokens available) ===")
    for i in range(1, 11):
        if limiter.allow_request():
            print(f"Request {i}: ALLOWED")
        else:
            print(f"Request {i}: BLOCKED")
        time.sleep(0.01)

    print("\n=== Waiting for tokens to refill... ===")
    time.sleep(2.5)

    print("=== After refill ===")
    for i in range(11, 18):
        if limiter.allow_request():
            print(f"Request {i}: ALLOWED")
        else:
            print(f"Request {i}: BLOCKED")
        time.sleep(0.01)


if __name__ == "__main__":
    main()
