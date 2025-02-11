# Create a CLI for the application

import json
from ot_croissant.crumbs.metadata import PlatformOutputMetadata
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--output",
    type=str,
    help="Output file path",
    required=True,
)


def app(output: str):
    """CLI for mlcroissant."""
    metadata = PlatformOutputMetadata()
    with open(output, "w") as f:
        content = metadata.to_json()
        content = json.dumps(content, indent=2)
        f.write(content)
        f.write("\n")  # Terminate file with newline


if __name__ == "__main__":
    app(parser.parse_args().output)
