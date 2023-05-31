import argparse

parser = argparse.ArgumentParser(description="Watnu: The personal task scheduler.")
parser.add_argument(
    "-e",
    "--experimental",
    action="store_true",
    help="Run in experimental mode.",
)

args = parser.parse_args()
if args.experimental:
    import src.main_experimental
else:
    import src.main  # noqa: F401
