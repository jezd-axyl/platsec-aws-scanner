from __future__ import annotations
from dataclasses import dataclass
from json import loads
from typing import Any, Callable, Dict, List, Optional


@dataclass
class Bucket:
    name: str
    data_sensitivity_tagging: Optional[BucketDataSensitivityTagging] = None
    encryption: Optional[BucketEncryption] = None
    logging: Optional[BucketLogging] = None
    public_access_block: Optional[BucketPublicAccessBlock] = None
    secure_transport: Optional[BucketSecureTransport] = None


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


@dataclass
class BucketSecureTransport:
    enabled: bool = False


def to_bucket_secure_transport(bucket_policy_dict: Dict[Any, Any]) -> BucketSecureTransport:
    statements = loads(str(bucket_policy_dict.get("Policy"))).get("Statement")
    return BucketSecureTransport(enabled=bool(list(filter(_has_secure_transport, statements))))


def _has_secure_transport(policy: Dict[Any, Any]) -> bool:
    return policy.get("Effect") == "Deny" and policy.get("Condition") == {"Bool": {"aws:SecureTransport": "false"}}


@dataclass
class BucketPublicAccessBlock:
    enabled: bool = False


def to_bucket_public_access_block(public_access_block_dict: Dict[str, Dict[str, bool]]) -> BucketPublicAccessBlock:
    config = public_access_block_dict["PublicAccessBlockConfiguration"]
    return BucketPublicAccessBlock(enabled=config["IgnorePublicAcls"] and config["RestrictPublicBuckets"])


@dataclass
class BucketDataSensitivityTagging:
    enabled: bool = False


def to_bucket_data_sensitivity_tagging(tagging_dict: Dict[str, List[Dict[str, str]]]) -> BucketDataSensitivityTagging:
    return BucketDataSensitivityTagging(enabled=_has_data_sensitivity_tagging(tagging_dict["TagSet"]))


def _has_data_sensitivity_tagging(tags: List[Dict[str, str]]) -> bool:
    return bool(list(filter(lambda tag: tag["Key"] == "data_sensitivity" and tag["Value"] in ["high", "low"], tags)))
