"""CLI entry point for running Atom AI as a module.

Usage:
    python -m atom          # Run the assistant
    python -m atom --help   # Show help
"""

import sys
import argparse


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        prog='atom',
        description='Atom AI - Intelligent Personal Assistant'
    )
    parser.add_argument(
        '--version', '-v',
        action='store_true',
        help='Show version and exit'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode (no speech)'
    )
    
    args = parser.parse_args()
    
    if args.version:
        from atom import __version__
        print(f"Atom AI v{__version__}")
        return 0
    
    # Import and run main application
    try:
        from atom.main import main as run_app
        import asyncio
        asyncio.run(run_app())
    except KeyboardInterrupt:
        print("\nGoodbye!")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
