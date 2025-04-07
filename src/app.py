# Create a CLI for the application
from pathlib import Path
import json
from ot_croissant.crumbs.metadata import PlatformOutputMetadata
import argparse
from datetime import datetime
import logging

def list_folders_in_directory(user_path: str) -> list[str]:
    """Generate a list of folders within the given directory with absolute paths.

    Args:
        user_path (str): The absolute or relative path provided by the user.

    Returns:
        list[str]: A list of absolute paths to the folders in the directory.
    """
    # Resolve the user-provided path to an absolute path
    directory = Path(user_path).expanduser().resolve()

    # Check if the path exists and is a directory
    if not directory.is_dir():
        raise ValueError(f"The provided path '{user_path}' is not a valid directory.")

    # List all folders in the directory and return their absolute paths
    return [str(folder.resolve()) for folder in directory.iterdir() if folder.is_dir()]


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
    required=False,
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
    required=False,
)
# Folder with the datasets:
parser.add_argument(
    "--dataset_folder",
    type=str,
    help="Folder with the datasets",
    required=False,
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

parser.add_argument(
    "--data_integrity_hash",
    type=str,
    help="Data integrity hash using sha256",
    required=True,
)


def datetime_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def main():
    """CLI for mlcroissant."""
    # Validate some arguments:
    if (parser.parse_args().dataset is None) and (parser.parse_args().dataset_folder is None):
        raise ValueError("At least one dataset of a folder with datasts must be provided.")
    
    # If no dataset folder provided use the directly specified datasets:
    if parser.parse_args().dataset_folder is None:
        datasets = parser.parse_args().dataset
    # If dataset folder is given, open folder and get a list of datasets:
    else:
        datasets = list_folders_in_directory(parser.parse_args().dataset_folder)

    metadata = PlatformOutputMetadata(
        ftp_location=parser.parse_args().ftp_location,
        datasets=datasets,
        version=parser.parse_args().version,
        date_published=datetime.fromisoformat(parser.parse_args().date_published),
        gcp_location=parser.parse_args().gcp_location,
        data_integrity_hash=parser.parse_args().data_integrity_hash,
    )
    with open(parser.parse_args().output, "w") as f:
        content = metadata.to_json()
        content = json.dumps(content, indent=2, default=datetime_serializer)
        f.write(content)
        f.write("\n")


if __name__ == "__main__":
    # Initialize logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    main()
