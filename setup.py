from setuptools import setup, find_packages

setup(
    name="translate-api",
    version="1.0.0",
    description="TranslateAPI Python SDK",
    author="ForceKeys",
    author_email="contact@forcekeys.com",
    url="https://github.com/forcekeys/translate-api-python",
    packages=find_packages(),
    install_requires=["requests>=2.25.0"],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    extras_require={
        "dev": ["pytest", "pytest-cov", "black", "flake8"],
    },
)
