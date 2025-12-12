# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.6] - 2025-12-12

### Fixed

- Fixed API key validation to raise `AuthenticationError` instead of `ValueError` for invalid format, ensuring consistent error handling

## [0.1.5] - 2025-12-12

### Fixed

- Fixed Pydantic validation errors when `citations.pages` or `citations.metadata` are returned as `null` from the API

## [0.1.4] - 2025-12-12

### Changed

- Updated API key prefix validation from `sk_live_` to `brainus_` to match backend changes

## [0.1.3] - 2025-12-12

### Changed

- Updated docs

## [0.1.2] - 2025-12-12

### Changed

- Updated docs

## [0.1.1] - 2025-12-12

### Changed

- Updated README to be minimalistic with links to full documentation
- Updated repository URLs to correct GitHub organization

## [0.1.0] - 2025-12-12

### Added

- Initial release
- Query endpoint with optional store_id, filters, and model parameters
- Usage statistics endpoint
- Plans listing endpoint
- Structured QueryFilters model
- Error handling for authentication, rate limits, and quotas
- Full type hints with Pydantic models
- Async/await support

[0.1.4]: https://github.com/BrainUsLK/brainus-ai-python/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/BrainUsLK/brainus-ai-python/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/BrainUsLK/brainus-ai-python/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/BrainUsLK/brainus-ai-python/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/BrainUsLK/brainus-ai-python/releases/tag/v0.1.0
