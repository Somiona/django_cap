# Release Checklist

## Pre-release
- [ ] Update version in `pyproject.toml`
- [ ] Update version in `__init__.py`
- [ ] Update `CHANGELOG.md` with new version details
- [ ] Run all tests: `uv run pytest`
- [ ] Run linting: `uv run ruff check`
- [ ] Run formatting: `uv run ruff format --check`
- [ ] Build package: `uv run pdm build`
- [ ] Check package: `uv run twine check dist/*.whl dist/*.tar.gz`
- [ ] Test installation in clean environment

## Release
- [ ] Create and push git tag: `git tag v0.1.0 && git push origin v0.1.0`
- [ ] Publish to PyPI: `uv run twine upload dist/*.whl dist/*.tar.gz`
- [ ] Create GitHub release with changelog
- [ ] Announce on relevant channels

## Post-release
- [ ] Update version to next development version (e.g., 0.1.1-dev)
- [ ] Update documentation if needed
- [ ] Test installation from PyPI: `pip install django-cap`
- [ ] Monitor for issues and feedback
