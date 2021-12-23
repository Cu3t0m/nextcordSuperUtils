from setuptools import setup

f = open("README.md", "r")
README = f.read()

setup(
    name="nextcordSuperUtils",
    packages=["nextcordSuperUtils"],
    package_data={
        "nextcordSuperUtils.assets": ["*"],
        "": ["*.png", "*.ttf"],
        "nextcordSuperUtils.music": ["*"],
        "nextcordSuperUtils.music.lavalink": ["*"],
    },
    include_package_data=True,
    version="0.3.0",
    license="MIT",
    description="Discord Bot Development made easy!",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Custom",
    url="https://github.com/Cu3t0m/nextcord-super-utils",
    download_url="https://github.com/Cu3t0m/nextcordsuperutils/archive/refs/tags/v0.3.0.tar.gz",
    keywords=[
        "nextcord",
        "easy",
        "nextcord.py",
        "music",
        "download",
        "links",
        "images",
        "videos",
        "audio",
        "bot",
        "paginator",
        "economy",
        "reaction",
        "reaction roles",
        "database",
        "database manager",
    ],
    install_requires=[
        "nextcord.py",
        "Pillow",
        "requests",
        "spotipy",
        "aiosqlite",
        "motor",
        "aiopg",
        "aiomysql",
        "nextcord_components",
        "pytz",
        "wavelink",
        "youtube_dl",
    ],
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        # Pick your license as you wish
        "License :: OSI Approved :: MIT License",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
)
