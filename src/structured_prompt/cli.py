#!/usr/bin/env python3
"""
Command-line interface for the Structured Prompt Framework.
"""

import argparse
import sys
from pathlib import Path

from .generator import PromptStructureGenerator


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="structured-prompt",
        description="Generate Python stage classes from YAML prompt structure definitions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate stages from YAML
  structured-prompt generate stages.yaml -o src/stages.py

  # With custom input/output paths
  structured-prompt generate config/prompt_structure.yaml -o myapp/prompts/stages.py
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate command
    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate Python stage classes from YAML",
        description="Generate Python stage classes from a YAML prompt structure definition",
    )
    generate_parser.add_argument(
        "input",
        type=str,
        help="Path to the input YAML file containing stage definitions",
    )
    generate_parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        help="Path where the generated Python file should be written",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "generate":
        try:
            input_path = Path(args.input)
            output_path = Path(args.output)

            if not input_path.exists():
                print(f"Error: Input file not found: {input_path}", file=sys.stderr)
                sys.exit(1)

            generator = PromptStructureGenerator(input_path)
            generator.generate(output_path)

            print(f"Successfully generated {output_path}")
            sys.exit(0)

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
