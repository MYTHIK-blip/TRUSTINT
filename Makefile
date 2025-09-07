.PHONY: setup lint test ingest export package chain-verify checksums

setup:
	pip install -r requirements.txt
	pip install -e .

lint:
	ruff check .
	mypy .

test:
	pytest -q

ingest:
	trustint ingest

export:
	trustint export

chain-verify:
	python scripts/prov_tools.py chain-verify

checksums:
	python scripts/prov_tools.py checksums

package:
	cd dist && tar -czf trustint-bronze-v0.1.tar.gz *.md *.csv *.jsonl SHA256SUMS
	cd dist && sha256sum trustint-bronze-v0.1.tar.gz > trustint-bronze-v0.1.sha256
