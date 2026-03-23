# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Updated

- Align catalog collections request handling with limit/token query parameters.

### Changed

### Removed

### Fixed

## [v0.1.2] - 2026-03-23

### Updated

- Added token, limit params to get_catalog_collections

## [v0.1.1] - 2026-03-23

### Fixed

- Fixed project name

## [v0.1.0] - 2026-03-22

### Added

- Initial release of the STAC FastAPI multi-tenant catalogs extension package.
- `CatalogsExtension` route registration for discovery and optional transaction
	endpoints.
- Core request/response models and types for catalogs and children APIs.
- Abstract client contract via `AsyncBaseCatalogsClient`.
- Test suite for extension routes and behavior.
- Packaging via `pyproject.toml` and local developer `Makefile` targets.
- GitHub workflows:
	- CI on pull requests and pushes to `main`.
	- PyPI publish workflow scoped to this repository and version tags.

### Changed

- README expanded with integration guidance, conformance class notes, support
	status table, and implementation references.

### Fixed

- `isort` and `black` hook configuration conflict resolved by aligning isort
	with the Black profile.


[Unreleased]: https://github.com/StacLabs/stac-fastapi-catalogs-extension/compare/v0.1.2...main
[v0.1.2]: https://github.com/StacLabs/stac-fastapi-catalogs-extension/compare/v0.1.1...v0.1.2
[v0.1.1]: https://github.com/StacLabs/stac-fastapi-catalogs-extension/compare/v0.1.0...v0.1.1
[v0.1.0]: https://github.com/StacLabs/stac-fastapi-catalogs-extension/releases/tag/v0.1.0
