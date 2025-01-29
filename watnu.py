import argparse

parser = argparse.ArgumentParser(description="Watnu: The Personal Task Scheduler.")
parser.add_argument(
    "-e",
    "--experimental",
    action="store_true",
    help="Run in experimental mode.",
)

args = parser.parse_args()
if args.experimental:
    import src.main_experimental  # noqa: F401
else:
    import src.main  # noqa: F401
