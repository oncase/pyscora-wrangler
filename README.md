# Pyscora Wrangler

<p align="center">
<img alt="Python versions" src="https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-brightgreen.svg">
<a href="https://github.com/oncase/pyscora-wrangler/blob/main/LICENSE"><img alt="License: MIT" src="https://black.readthedocs.io/en/stable/_static/license.svg"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a></p>

Python package that consists mainly of wrappers for Data Engineering tasks.

In order to see the docs, click on the module that you want inside the folder `pyscora_wrangler/${MODULE}`

## Installation

```sh
pip install pyscora-wrangler
```

## Local Development

### Dependencies:

- Python >=3.8, <4.0
- Poetry >=1.4.0

### Instructions

- Create a virtual environment, an example is shown below:

```sh
virtualenv -p python3 venv && source venv/bin/activate
```

- Install the necessary packages:

```sh
  pip install "poetry==1.4.2" # or any other version greater or equal than 1.4.0
  poetry install
```

Now you are ready! To test the changes, create a `test.py` file at the root level and run it.

## How is it published?

When any changes are pushed to `main`, the GitHub Actions automatically deploys the new version.

Before committing the changes, remember to:

- Change the **title** and **automatic_release_tag** at `.github/workflows/publish.yml`.
- Change the **version** at `pyproject.toml`.
