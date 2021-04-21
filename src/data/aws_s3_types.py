from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional


@dataclass
class Bucket:
    name: str
    encryption: Optional[BucketEncryption] = None
    logging: Optional[BucketLogging] = None


def to_bucket(bucket_dict: Dict[Any, Any]) -> Bucket:
    return Bucket(name=bucket_dict["Name"])


@dataclass
class BucketEncryption:
    enabled: bool = False
    type: Optional[str] = None


def to_bucket_encryption(encryption_dict: Dict[Any, Any]) -> BucketEncryption:
    sse_config = encryption_dict["ServerSideEncryptionConfiguration"]["Rules"][0]["ApplyServerSideEncryptionByDefault"]
    algorithm = sse_config.get("SSEAlgorithm")
    key = sse_config.get("KMSMasterKeyID")

    algo_mapping: Dict[str, Callable[[], BucketEncryption]] = {
        "AES256": lambda: BucketEncryption(enabled=True, type="aes"),
        "aws:kms": lambda: BucketEncryption(enabled=True, type="aws" if not key or "alias/aws/" in key else "cmk"),
    }

    return algo_mapping[algorithm]()


@dataclass
class BucketLogging:
    enabled: bool = False


def to_bucket_logging(logging_dict: Dict[Any, Any]) -> BucketLogging:
    return BucketLogging(enabled="LoggingEnabled" in logging_dict)
