# Changelog

## [0.5.0] - 2025-05-31

### Changed
- **BREAKING**: Made `sentence-transformers` and `chromadb` optional dependencies
  - Basic installation no longer includes ML/PyTorch dependencies (~50MB vs ~2GB)
  - Semantic search features now require `pip install cased-kit[ml]`
  - Full installation available via `pip install cased-kit[all]`

### Added
- New installation options for different use cases
- Comprehensive PR reviewer documentation at `/pr-reviewer`
- CI/CD integration examples for GitHub Actions

### Fixed
- Corrected PR review pricing documentation (actual: $0.01-0.05, not $0.10-0.30)
- Removed references to deprecated Simple mode

### Improved
- PR reviewer now shows model information in logs
- Added real-world PR review examples with actual costs
- Enhanced documentation organization 