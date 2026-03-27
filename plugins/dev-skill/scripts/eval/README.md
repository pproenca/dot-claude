# Eval Scripts

Python scripts for functional testing and description optimization of skills. Adopted from [Anthropic's official skill-creator plugin](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator) with import path adjustments.

## Dependencies

**Required for all eval scripts:**
- Python 3.10+

**Required for trigger evaluation (`run_eval.py`):**
- `claude` CLI installed and on PATH

**Required for description optimization (`improve_description.py`, `run_loop.py`):**
- `anthropic` Python package: `pip install anthropic`
- `ANTHROPIC_API_KEY` environment variable set

## Scripts

| Script | Purpose | CLI Usage |
|--------|---------|-----------|
| `run_eval.py` | Test whether a description triggers correctly | `python -m scripts.eval.run_eval --eval-set queries.json --skill-path ./skill` |
| `improve_description.py` | Generate improved description using Claude + extended thinking | `python -m scripts.eval.improve_description --eval-results results.json --skill-path ./skill --model claude-sonnet-4-20250514` |
| `run_loop.py` | Full eval+improve loop with train/test split | `python -m scripts.eval.run_loop --eval-set queries.json --skill-path ./skill --model claude-sonnet-4-20250514 --max-iterations 5` |
| `aggregate_benchmark.py` | Aggregate grading results into benchmark stats | `python -m scripts.eval.aggregate_benchmark ./workspace/iteration-1 --skill-name my-skill` |
| `generate_report.py` | Generate HTML report from benchmark data | Used internally by `run_loop.py` |
| `package_skill.py` | Package skill as distributable .skill file | `python -m scripts.eval.package_skill ./path/to/skill` |
| `quick_validate.py` | Basic frontmatter validation | `python -m scripts.eval.quick_validate ./path/to/skill` |
| `utils.py` | Shared utilities (parse_skill_md) | Library, not CLI |

## License

These scripts are derived from Anthropic's claude-plugins-official repository. See `LICENSE.txt` in this directory.
