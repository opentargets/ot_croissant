# Create a CLI for the application

import json
from ot_croissant.crumbs.metadata import PlatformOutputMetadata
import argparse
from datetime import datetime

parser = argparse.ArgumentParser()
# Output file path
parser.add_argument(
    "--output",
    type=str,
    help="Output file path",
    required=True,
)
# FTP location
parser.add_argument(
    "--ftp_location",
    type=str,
    help="FTP location",
    required=True,
)
parser.add_argument(
    "--gcp_location",
    type=str,
    help="GCP location",
    required=True,
)
# List of datasets to include
parser.add_argument(
    "-d",
    "--dataset",
    action="append",
    type=str,
    help="Dataset to include",
    required=True,
)
# Data release version
parser.add_argument(
    "--version",
    type=str,
    help="Data release version",
    required=True,
)

parser.add_argument(
    "--date_published",
    type=str,
    help="Data release date in ISO 8601 format (https://en.wikipedia.org/wiki/ISO_8601)",
    required=True,
)


def datetime_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def main():
    """CLI for mlcroissant."""
    metadata = PlatformOutputMetadata(
        ftp_location=parser.parse_args().ftp_location,
        datasets=parser.parse_args().dataset,
        version=parser.parse_args().version,
        date_published=datetime.fromisoformat(parser.parse_args().date_published),
        gcp_location=parser.parse_args().gcp_location,
    )
    with open(parser.parse_args().output, "w") as f:
        content = metadata.to_json()
        content = json.dumps(content, indent=2, default=datetime_serializer)
        f.write(content)
        f.write("\n")


if __name__ == "__main__":
    main()
