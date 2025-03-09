from setuptools import setup, find_packages
import os
import subprocess

def post_install():
    subprocess.run(["python", "langsentry/post_install.py"], check=True)

setup(
    name="langsentry",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "spacy",
        "google-genai",
        "pyperclip",
        "sentence_transformers",
        "pandas",
        "numpy",
    ],
    author="Edwin, Keith, Max, Tim, Zeph",
    author_email="NIL",
    description="Python-base security module designed to detect and prevent prompt injection attacks in Large Language Model",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/kabinet01/LangSentry",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
