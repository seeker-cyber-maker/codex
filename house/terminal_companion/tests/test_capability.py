from __future__ import annotations

import threading
import unittest

from house.terminal_companion.capability import (
    CapabilityValidationError,
    LoopbackCapabilityValidator,
)

NOW = 123_000_000_000
AUDIENCE = "com.codex.house.terminal-companion"


def entropy(value: int):
    return lambda size: bytes([value]) * size


class CapabilityTests(unittest.TestCase):
    def test_ipv4_capability_is_single_use_and_receipt_has_no_bearer(self) -> None:
        validator = LoopbackCapabilityValidator(entropy=entropy(1))
        grant = validator.issue(
            host="127.0.0.1", port=49152, now_ns=NOW, ttl_seconds=30
        )
        receipt = validator.consume(
            url=grant.url,
            method="GET",
            origin=None,
            audience=grant.audience,
            now_ns=NOW + 1,
        )

        self.assertEqual(
            receipt,
            {
                "schema": "codex-house-iterm-capability-consumption/1",
                "capability_id": "2e4268c98b2bff49488f0dc14a1adf8cf8ded0dc93ed89dd4bc4ef011d8e2df5",
                "audience": AUDIENCE,
                "authority": "127.0.0.1:49152",
                "method": "GET",
                "consumed_at_ns": NOW + 1,
                "expires_at_ns": NOW + 30_000_000_000,
                "transport": "NOT_ATTEMPTED",
                "iterm_api_registration": "NOT_ATTEMPTED",
                "terminal_input": "PROHIBITED",
                "receipt_id": "29959e7d693caf0b5acb8a08fabbc1bfa5e3310c949cd270969eb911109b1942",
            },
        )
        self.assertNotIn(grant.url.rsplit("/", 1)[-1], str(receipt))
        self.assertNotIn(grant.url.rsplit("/", 1)[-1], repr(grant))
        with self.assertRaises(CapabilityValidationError) as replay:
            validator.consume(
                url=grant.url,
                method="GET",
                origin=None,
                audience=grant.audience,
                now_ns=NOW + 2,
            )
        self.assertEqual(replay.exception.code, "REPLAYED_CAPABILITY")
        self.assertEqual(str(replay.exception), "capability rejected")

    def test_ipv6_uses_one_exact_canonical_authority(self) -> None:
        validator = LoopbackCapabilityValidator(entropy=entropy(2))
        grant = validator.issue(host="::1", port=49153, now_ns=NOW, ttl_seconds=5)
        self.assertTrue(grant.url.startswith("http://[::1]:49153/v1/display/"))
        receipt = validator.consume(
            url=grant.url,
            method="GET",
            origin=None,
            audience=AUDIENCE,
            now_ns=NOW,
        )
        self.assertEqual(receipt["authority"], "[::1]:49153")

    def test_noncanonical_or_nonloopback_hosts_and_ports_fail_closed(self) -> None:
        invalid_hosts = (
            "localhost",
            "127.0.0.2",
            "127.000.000.001",
            "2130706433",
            "::ffff:127.0.0.1",
            "0:0:0:0:0:0:0:1",
        )
        for index, host in enumerate(invalid_hosts):
            with self.subTest(host=host), self.assertRaises(CapabilityValidationError):
                LoopbackCapabilityValidator(entropy=entropy(index)).issue(
                    host=host, port=49152, now_ns=NOW, ttl_seconds=5
                )
        for port in (80, 0, 65536, True):
            with self.subTest(port=port), self.assertRaises(CapabilityValidationError):
                LoopbackCapabilityValidator(entropy=entropy(9)).issue(
                    host="127.0.0.1", port=port, now_ns=NOW, ttl_seconds=5
                )

    def test_url_ambiguity_and_suffixes_fail_without_consuming(self) -> None:
        validator = LoopbackCapabilityValidator(entropy=entropy(3))
        grant = validator.issue(host="127.0.0.1", port=49154, now_ns=NOW, ttl_seconds=5)
        token = grant.url.rsplit("/", 1)[-1]
        invalid_urls = (
            grant.url.replace("http://", "https://"),
            f"http://user@127.0.0.1:49154/v1/display/{token}",
            f"http://127.0.0.1:49154/v1/display/{token}?x=1",
            f"http://127.0.0.1:49154/v1/display/{token}#x",
            f"http://127.0.0.1:49154//v1/display/{token}",
            f"http://127.0.0.1:49154/v1/display/%41{token[1:]}",
            f"http://127.0.0.1:49154/v1/display/{token}/extra",
            f"http://127.0.0.1:049154/v1/display/{token}",
            f"\nhttp://127.0.0.1:49154/v1/display/{token}",
            f"HTTP://127.0.0.1:49154/v1/display/{token}",
        )
        for url in invalid_urls:
            with self.subTest(url=url), self.assertRaises(CapabilityValidationError):
                validator.consume(
                    url=url,
                    method="GET",
                    origin=None,
                    audience=AUDIENCE,
                    now_ns=NOW,
                )
        validator.consume(
            url=grant.url,
            method="GET",
            origin=None,
            audience=AUDIENCE,
            now_ns=NOW,
        )

    def test_method_origin_and_audience_reject_before_consumption(self) -> None:
        validator = LoopbackCapabilityValidator(entropy=entropy(4))
        grant = validator.issue(host="127.0.0.1", port=49155, now_ns=NOW, ttl_seconds=5)
        invalid = (
            {"method": "POST", "origin": None, "audience": AUDIENCE},
            {
                "method": "GET",
                "origin": "http://127.0.0.1:49155",
                "audience": AUDIENCE,
            },
            {"method": "GET", "origin": "null", "audience": AUDIENCE},
            {"method": "GET", "origin": None, "audience": "another-viewer"},
        )
        for request in invalid:
            with (
                self.subTest(request=request),
                self.assertRaises(CapabilityValidationError),
            ):
                validator.consume(url=grant.url, now_ns=NOW, **request)
        validator.consume(
            url=grant.url,
            method="GET",
            origin=None,
            audience=AUDIENCE,
            now_ns=NOW,
        )

    def test_expiry_clock_rollback_ttl_and_capacity_are_bounded(self) -> None:
        validator = LoopbackCapabilityValidator(entropy=entropy(5), max_records=1)
        grant = validator.issue(host="127.0.0.1", port=49156, now_ns=NOW, ttl_seconds=1)
        with self.assertRaises(CapabilityValidationError) as rollback:
            validator.consume(
                url=grant.url,
                method="GET",
                origin=None,
                audience=AUDIENCE,
                now_ns=NOW - 1,
            )
        self.assertEqual(rollback.exception.code, "CLOCK_ROLLBACK")
        with self.assertRaises(CapabilityValidationError) as full:
            validator.issue(host="127.0.0.1", port=49156, now_ns=NOW, ttl_seconds=1)
        self.assertEqual(full.exception.code, "CAPACITY_EXHAUSTED")
        with self.assertRaises(CapabilityValidationError) as expired:
            validator.consume(
                url=grant.url,
                method="GET",
                origin=None,
                audience=AUDIENCE,
                now_ns=NOW + 1_000_000_000,
            )
        self.assertEqual(expired.exception.code, "EXPIRED_CAPABILITY")
        self.assertEqual(validator.active_record_count(now_ns=NOW + 2_000_000_000), 0)
        validator.issue(
            host="127.0.0.1",
            port=49156,
            now_ns=NOW + 2_000_000_000,
            ttl_seconds=1,
        )
        with self.assertRaises(CapabilityValidationError) as ttl:
            LoopbackCapabilityValidator(entropy=entropy(6)).issue(
                host="127.0.0.1", port=49156, now_ns=NOW, ttl_seconds=301
            )
        self.assertEqual(ttl.exception.code, "TTL_EXCEEDS_LIMIT")

    def test_entropy_shape_and_collision_fail_closed(self) -> None:
        with self.assertRaises(CapabilityValidationError) as shape:
            LoopbackCapabilityValidator(entropy=lambda size: b"short").issue(
                host="127.0.0.1", port=49157, now_ns=NOW, ttl_seconds=1
            )
        self.assertEqual(shape.exception.code, "INVALID_ENTROPY")

        validator = LoopbackCapabilityValidator(entropy=entropy(7))
        validator.issue(host="127.0.0.1", port=49157, now_ns=NOW, ttl_seconds=1)
        with self.assertRaises(CapabilityValidationError) as collision:
            validator.issue(host="127.0.0.1", port=49157, now_ns=NOW, ttl_seconds=1)
        self.assertEqual(collision.exception.code, "TOKEN_COLLISION")

    def test_concurrent_consumers_admit_exactly_one(self) -> None:
        validator = LoopbackCapabilityValidator(entropy=entropy(8))
        grant = validator.issue(host="127.0.0.1", port=49158, now_ns=NOW, ttl_seconds=5)
        outcomes: list[str] = []
        barrier = threading.Barrier(3)

        def consume() -> None:
            barrier.wait()
            try:
                validator.consume(
                    url=grant.url,
                    method="GET",
                    origin=None,
                    audience=AUDIENCE,
                    now_ns=NOW,
                )
                outcomes.append("accepted")
            except CapabilityValidationError as exc:
                outcomes.append(exc.code)

        threads = [threading.Thread(target=consume) for _ in range(2)]
        for thread in threads:
            thread.start()
        barrier.wait()
        for thread in threads:
            thread.join()
        self.assertEqual(sorted(outcomes), ["REPLAYED_CAPABILITY", "accepted"])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
