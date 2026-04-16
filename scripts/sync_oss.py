#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from urllib.parse import quote

import oss2

try:
    import oss_config
except ImportError:
    oss_config = None


DEFAULT_SOURCE_DIR = Path(
    getattr(oss_config, "SOURCE_DIR", "~/.m2/repository/ru/bartwell/kick"),
).expanduser()
DEFAULT_PREFIX = getattr(oss_config, "PREFIX", "")
DEFAULT_PUBLIC_URL = getattr(oss_config, "PUBLIC_URL", "")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Recursively upload local Maven artifacts to Aliyun OSS.",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE_DIR,
        help=f"Local directory to upload recursively. Default: {DEFAULT_SOURCE_DIR}",
    )
    parser.add_argument(
        "--prefix",
        default=DEFAULT_PREFIX,
        help="Remote OSS key prefix. Example: maven/ru/bartwell/kick",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Upload even if the remote object already exists with the same size.",
    )
    parser.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        default=True,
        help="Preview uploads without writing to OSS. Enabled by default.",
    )
    parser.add_argument(
        "--execute",
        dest="dry_run",
        action="store_false",
        help="Actually upload files to OSS.",
    )
    return parser.parse_args()


def require_env(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    print(f"Missing required environment variable: {name}", file=sys.stderr)
    sys.exit(1)


def require_config(name: str, env_name: str) -> str:
    value = getattr(oss_config, name, "") if oss_config else ""
    if value:
        return value
    return require_env(env_name)


def build_bucket() -> oss2.Bucket:
    auth = oss2.Auth(
        require_config("ACCESS_KEY_ID", "ALIYUN_OSS_ACCESS_KEY_ID"),
        require_config("ACCESS_KEY_SECRET", "ALIYUN_OSS_ACCESS_KEY_SECRET"),
    )
    endpoint = require_config("ENDPOINT", "ALIYUN_OSS_ENDPOINT")
    bucket_name = require_config("BUCKET", "ALIYUN_OSS_BUCKET")
    return oss2.Bucket(auth, endpoint, bucket_name)


def normalize_prefix(prefix: str) -> str:
    return prefix.strip("/")


def build_object_key(prefix: str, source_root: Path, file_path: Path) -> str:
    relative_path = file_path.relative_to(source_root).as_posix()
    if not prefix:
        return relative_path
    return f"{prefix}/{relative_path}"


def build_public_url(object_key: str) -> str:
    public_url = DEFAULT_PUBLIC_URL.strip().rstrip("/")
    if not public_url:
        return ""
    return f"{public_url}/{quote(object_key, safe='/')}"


def remote_same_size(bucket: oss2.Bucket, object_key: str, local_size: int) -> bool:
    try:
        meta = bucket.head_object(object_key)
    except oss2.exceptions.NoSuchKey:
        return False
    except oss2.exceptions.OssError as exc:
        print(f"Failed to inspect remote object {object_key}: {exc}", file=sys.stderr)
        raise
    return meta.content_length == local_size


def iter_files(source_root: Path) -> list[Path]:
    return sorted(path for path in source_root.rglob("*") if path.is_file())


def main() -> int:
    args = parse_args()
    source_root = args.source.expanduser().resolve()
    prefix = normalize_prefix(args.prefix)

    if not source_root.exists():
        print(f"Source directory does not exist: {source_root}", file=sys.stderr)
        return 1
    if not source_root.is_dir():
        print(f"Source path is not a directory: {source_root}", file=sys.stderr)
        return 1

    bucket = build_bucket()
    files = iter_files(source_root)

    if not files:
        print(f"No files found under: {source_root}")
        return 0

    uploaded = 0
    skipped = 0

    for file_path in files:
        object_key = build_object_key(prefix, source_root, file_path)
        file_size = file_path.stat().st_size
        public_url = build_public_url(object_key)

        if not args.force and remote_same_size(bucket, object_key, file_size):
            print(f"skip   {object_key}")
            if public_url:
                print(f"       {public_url}")
            skipped += 1
            continue

        action = "dry-run" if args.dry_run else "upload"
        print(f"{action} {object_key}")
        if not args.dry_run:
            bucket.put_object_from_file(object_key, str(file_path))
        if public_url:
            print(f"       {public_url}")
        uploaded += 1

    print(f"Done. uploaded={uploaded} skipped={skipped} total={len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
