"""
Main module to run the application:
python3 -m app -c config.json
"""

import sys

if __name__ == "__main__":
    from app.main import main

    sys.exit(main())  # pylint: disable=no-value-for-parameter
