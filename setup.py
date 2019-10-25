import os

from setuptools import setup


def readme():
    with open(os.path.join(os.path.dirname(__file__), "README.md")) as handle:
        return handle.read()


if __name__ == "__main__":
    setup(
        name="miscutils",
        version="0.1.0",
        license="MIT",
        url="https://github.com/dustinrohde/miscutils",
        description="Miscellaneous Python utilities.",
        long_description=readme(),
        include_package_data=True,
        packages=["miscutils"],
    )
