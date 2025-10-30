"""mp4_to_srv3 setup."""
from __future__ import annotations

__all__: list[str] = []

from pathlib import Path

# pylint: disable-next=E0401
from setuptools import setup  # type: ignore

if __name__ == "__main__":
    setup(
        name="mp4_to_srv3",
        version="0.0.1",
        description="Convert mp4 to srv3 subtitles using ASCII art.",
        long_description=Path("README.md").read_text(encoding="utf-8"),
        long_description_content_type="text/markdown",
        author="Nice Zombies",
        author_email="nineteendo19d0@gmail.com",
        maintainer="Nice Zombies",
        maintainer_email="nineteendo19d0@gmail.com",
        packages=["mp4_to_srv3"],
        classifiers=[
            "Development Status :: 4 - Beta",
            "Programming Language :: Python :: 3 :: Only",
        ],
        license="GPL-3.0",
        keywords=["python"],
        package_dir={"": "src"},
        # setuptools arguments
        install_requires=Path("requirements.txt").read_text(encoding="utf-8"),
        entry_points={
            "console_scripts": ["mp4_to_srv3 = mp4_to_srv3.__main__:main"]
        },
        project_urls={
            "Homepage": "https://github.com/nineteendo/mp4_to_srv3",
            "Issues": "https://github.com/nineteendo/mp4_to_srv3/issues",
            "Sponser": "https://paypal.me/nineteendo",
        },
    )
