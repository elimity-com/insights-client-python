import setuptools

setuptools.setup(
    name="Elimity Insights Python client",
    version="0.0.1",
    author="Elimity",
    author_email="tom@elimity.com",
    description="Client acting as a wrapper of the Elimity Insights API which can be used by import scripts.",
    url="https://github.com/elimity-com/insights-client-python",
    packages=['insights_client'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
