"""
Compatibility wrapper for the France-first build.

The original script merged US BLS CSV rows with scores.json. The current
project uses verified Eurostat France data and writes the same site/data.json
shape through build_fr_dataset.py.

Usage:
    python build_site_data.py
"""

from build_fr_dataset import main


if __name__ == "__main__":
    main()
