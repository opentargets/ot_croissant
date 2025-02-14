# Create a CLI for the application

import json
from ot_croissant.crumbs.metadata import PlatformOutputMetadata
import argparse

parser = argparse.ArgumentParser()
# Output file path
parser.add_argument(
    "--output",
    type=str,
    help="Output file path",
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


def main():
    """CLI for mlcroissant."""
    metadata = PlatformOutputMetadata(datasets=parser.parse_args().dataset)
    with open(parser.parse_args().output, "w") as f:
        content = metadata.to_json()
        content = json.dumps(content, indent=2)
        f.write(content)
        f.write("\n")


if __name__ == "__main__":
    main()
