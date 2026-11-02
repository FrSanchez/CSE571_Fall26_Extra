# Repository Guidelines

## Project Structure & Module Organization

This directory currently contains `CSE571_Fall26.pdf`. It has no source modules, test suite, asset directories, or build configuration. Keep the PDF at the root and preserve its filename unless a change is explicitly requested.

When adding coursework, group related files by assignment or topic, for example `assignments/assignment_01/`. Keep supporting assets with the work that uses them. Introduce shared `src/` or `tests/` directories only when the project needs them, and document new directories in a README.

## Build, Test, and Development Commands

No build, test, lint, or local server commands are configured. Do not assume that `npm test`, `make build`, or similar commands apply.

Use `ls -la` to inspect the directory and `rg --files` to list files. If executable code is introduced, document its prerequisites, dependency installation, run command, and test command alongside that code before relying on those workflows.

## Coding Style & Naming Conventions

Use descriptive filenames and consistent naming within each assignment. For new directories and scripts, prefer lowercase names with underscores, such as `assignment_01` or `search_demo.py`. Preserve supplied course-material filenames.

Use Markdown headings and short, actionable paragraphs for documentation. No language-specific indentation standard, formatter, or linter is configured; establish and document those conventions when introducing a language.

## Testing Guidelines

No testing framework or coverage threshold exists. Verify documentation links and paths, and confirm that added or replaced PDFs open correctly. For future code, add tests for expected behavior and edge cases, describe how to run them, and follow the selected framework’s naming conventions.

## Commit & Pull Request Guidelines

This directory is not currently a Git repository, so no commit-message conventions can be inferred. If version control is introduced, use concise, imperative messages such as `Add assignment 01 notes`.

Pull requests should explain the purpose, list affected assignments or documents, and describe validation performed. Link relevant issues when available; include screenshots only when they clarify a visual change.
