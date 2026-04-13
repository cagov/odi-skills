SKILL ?= odi-plain-language

.PHONY: skill skill-release lint format check

# Package a skill non-interactively (see docs/PACKAGE-SKILL.md)
skill:
	python3 scripts/package_skill.py $(SKILL) --no-prompt

# Package a skill; prompts to copy artifact to releases/
skill-release:
	python3 scripts/package_skill.py $(SKILL)

lint:
	npx biome ci .
	ruff check scripts src

format:
	npx biome check --write .
	ruff format scripts src

check: lint
