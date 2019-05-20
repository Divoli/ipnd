from setuptools import setup

with open("README.md") as f:
    long_description = f.read()

setup(
    name="au-ipnd",
    description="Australian IPND Client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version="0.0.2",
    url="https://github.com/Divoli/ipnd",
    author="Devoli",
    author_email="dev@devoli.com",
    license="AGPL 3",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
    ],
    packages=["ipnd"],
    install_requires=[],
)
