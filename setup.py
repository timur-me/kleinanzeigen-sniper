from setuptools import find_packages, setup

from app import __version__

setup(
    name="kleinanzeigen-sniper",
    version=__version__,
    description="A Telegram bot for monitoring and notifying about new listings on Kleinanzeigen.de",
    author="Kleinanzeigen Sniper Team",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "aiogram>=3.0.0",
        "aiohttp>=3.8.5",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "loguru>=0.7.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
) 