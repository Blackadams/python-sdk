import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="elarian",
    version="0.0.0",
    description="Official Elarian Python SDK",
    long_description=README,
    long_description_content_type="text/markdown",
    keywords="elarian africastalking sms ussd voice customer payments",
    url="https://github.com/ElarianLtd/python-sdk",
    author="Elarian",
    author_email="info@elarian.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(exclude=("test",)),
    include_package_data=True,
    install_requires=["grpcio"],
)