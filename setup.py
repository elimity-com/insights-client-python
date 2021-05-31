"""Setup module for the Elimity Insights client."""

from setuptools import setup

_classifiers = [
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3.6",
]

_install_requires = ["python-dateutil", "requests", "simplejson"]

with open("README.md") as file:
    _long_description = file.read()

setup(
    author="Elimity development team",
    author_email="dev@elimity.com",
    classifiers=_classifiers,
    description="Client for connector interactions with an Elimity Insights server",
    install_requires=_install_requires,
    license="Apache-2.0",
    long_description=_long_description,
    long_description_content_type="text/markdown",
    name="elimity-insights-client",
    python_requires=">=3.7",
    py_modules=["elimity_insights_client"],
    url="https://github.com/elimity-com/insights-client-python",
    version="8.0.0a0",
)
