"""Unified entry point for TikTokAutoUploader.

This module dispatches to either the command line interface or the GUI
implementation.  By default the CLI is executed; passing ``--gui`` will
launch the graphical interface.
"""
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="TikTokAutoUploader application")
    parser.add_argument(
        "--gui", action="store_true", help="Run the graphical interface instead of the CLI"
    )
    args, remainder = parser.parse_known_args()

    if args.gui:
        # Import lazily to avoid Qt dependency when running purely via CLI
        from tiktok_uploader.gui_app import run_gui

        run_gui()
    else:
        from cli import main as cli_main

        cli_main(remainder)


if __name__ == "__main__":
    main()
