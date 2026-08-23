# Contributing

## Setup

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install prek
uv sync
prek install
```

`uv sync` downloads the Python version pinned in `.python-version` if it is not already installed.

## Changing colours

Colours live in `palette.json` and nowhere else. Edit a hex there, then rebuild:

```sh
uv run main.py
```

## Checks

`prek run --all-files` runs json, whitespace, zizmor, ruff, ty, rumdl and the build. It also runs on commit once installed.

## Commits

Conventional Commits, subject line only: `type: subject`, lowercase, imperative. Types: feat, fix, docs, style, refactor, chore, ci. The commit-msg hook rejects anything else.

## Releases

Releases are automated with release-please. Each push to `master` updates a release pull request from the commits since the last tag. Merging it bumps `version` in `pyproject.toml` and `palette.json`, updates `CHANGELOG.md`, tags, and publishes a GitHub release with `orikalk.zip` and `orikalk.tar.gz`.

The repository setting "Allow GitHub Actions to create and approve pull requests" must be on. The default token cannot trigger workflows, so the check workflow does not run on the release pull request unless a `RELEASE_PLEASE_TOKEN` repository secret holds a fine-grained PAT with contents and pull requests write access.
