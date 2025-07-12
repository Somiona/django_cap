# Release Checklist

## Pre-release
- [ ] Update version in `pyproject.toml`
- [ ] Update version in `__init__.py`
- [ ] Update `CHANGELOG.md` with new version details
- [ ] Run all tests: `pdm test`
- [ ] Run linting: `pdm lint-fix`
- [ ] Run formatting: `pdm format`
- [ ] Build package: `uv build`
- [ ] Check package: `pdm twine`
- [ ] Test installation in clean environment

## Release
- [ ] Create and push git tag: `git tag 0.2.0 && git push --tags`

## Post-release
- [ ] Update documentation if needed
- [ ] Test installation from PyPI: `pip install django-cap`
- [ ] Monitor for issues and feedback
