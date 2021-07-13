import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="elarian",
    version="0.0.4",
    description="Official Elarian Python SDK",
    long_description=README,
    long_description_content_type="text/markdown",
    keywords="elarian africastalking sms ussd voice customer payments",
    url="https://github.com/ElarianLtd/python-sdk",
    author="Elarian",
    author_email="salama@elarian.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.9",
    ],
    package_dir={
        '': 'src',
        'rsocket': 'lib/rsocket/rsocket',
        'reactivestreams': 'lib/rsocket/reactivestreams'
    },
    packages=[
        'elarian',
        'rsocket',
        'elarian.utils',
        'elarian.models',
        'reactivestreams',
        'elarian.utils.generated',
    ],
    include_package_data=True,
    install_requires=[
        'protobuf==3.15.6',
    ],
    python_requires=">=3.7",
)
