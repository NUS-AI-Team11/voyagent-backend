#!/usr/bin/env python
"""
VoyageAgent - main entry point
"""

import logging
import sys
from pathlib import Path

# Ensure the project root is on the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from orchestrator.workflow import TravelPlanningWorkflow


def setup_logging():
    """Configure the logging system."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('voyagent.log')
        ]
    )


def main():
    """Main function."""
    setup_logging()

    print("\n" + "=" * 60)
    print("VoyageAgent - Intelligent Travel Planning System")
    print("=" * 60 + "\n")

    workflow = TravelPlanningWorkflow()

    print("Enter your travel requirements (multi-line input, type 'END' to finish):\n")
    lines = []
    while True:
        line = input()
        if line.strip().upper() == 'END':
            break
        lines.append(line)

    user_input = '\n'.join(lines)

    if not user_input.strip():
        print("No input provided. Exiting.")
        return

    try:
        context = workflow.run(user_input)

        if context.final_handbook:
            print("\nPlanning complete.")
            print(f"Travel handbook: {context.final_handbook.title}")
        else:
            print("\nPlanning encountered issues.")
            if context.errors:
                print("Errors:")
                for error in context.errors:
                    print(f"  - {error}")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        logging.exception("Unhandled exception")
        sys.exit(1)


if __name__ == "__main__":
    main()
