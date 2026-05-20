import time
import unittest

from rate_limiter import TokenBucketRateLimiter


class TestTokenBucketRateLimiter(unittest.TestCase):

    def test_allow_request_within_capacity(self):
        limiter = TokenBucketRateLimiter(capacity=5, refill_rate=10)
        for _ in range(5):
            self.assertTrue(limiter.allow_request())

    def test_block_request_when_exceeded(self):
        limiter = TokenBucketRateLimiter(capacity=3, refill_rate=10)
        for _ in range(3):
            limiter.allow_request()
        self.assertFalse(limiter.allow_request())

    def test_refill_restores_tokens(self):
        limiter = TokenBucketRateLimiter(capacity=5, refill_rate=10)
        for _ in range(5):
            limiter.allow_request()
        self.assertFalse(limiter.allow_request())
        time.sleep(0.2)
        self.assertTrue(limiter.allow_request())


if __name__ == "__main__":
    unittest.main()
