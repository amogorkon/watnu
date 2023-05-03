import argparse

parser = argparse.ArgumentParser(description="Watnu: The personal task scheduler.")
parser.add_argument("-t", "--testing", action="store_true", help="Run in test mode.")

args = parser.parse_args()
if args.testing:
    import src.testing
else:
    import src.main
