# Day 10 — Thumbnail Recipe Evidence

## Repository

SamanthaNabila/pyffmpegcore
link:https://github.com/SamanthaNabila/pyffmpegcore

## Commit

`f12a098` — `docs: strengthen thumbnail recipe evidence`

## Changed Files

- `docs/recipes/thumbnails.md`
- `tests/test_cli_thumbnail_real.py`

## Validation

- Focused tests: **6 passed**
- Documentation check: **passed**
- `git diff --check`: **passed**

## Real-Media Verification

The real-media fixture was generated locally after installing FFmpeg/FFprobe.

No generated media or receipts were committed to the repository.

## Summary

The thumbnail recipe documentation was strengthened with:

- Deterministic fixture generation
- 640px JPEG thumbnail generation
- Machine-readable result output
- MJPEG and width verification
- Receipt generation and validation
- Overwrite refusal verification
- `--force` replacement verification
- A focused real-media acceptance test
