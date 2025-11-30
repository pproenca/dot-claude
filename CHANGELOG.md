# Changelog

## [3.2.0](https://github.com/pproenca/dot-claude/compare/v3.1.0...v3.2.0) (2025-11-30)


### Features

* **blackbox:** add hooks configuration ([28e1b18](https://github.com/pproenca/dot-claude/commit/28e1b1898be37c52526d505df6ce151adcdb53f1))
* **blackbox:** add plugin manifest ([e79a91b](https://github.com/pproenca/dot-claude/commit/e79a91b9b8b088a56aaf8e4c5ba28717ebbccf61))
* **blackbox:** add TOCTOU protection, immutability, and fsync ([0b5fece](https://github.com/pproenca/dot-claude/commit/0b5fece3e4f52816a48adbf1f963fa5e1182e539))
* **blackbox:** complete implementation per PRD v5.0 ([1003e92](https://github.com/pproenca/dot-claude/commit/1003e92cb07413dd693ef84293a55cb8a1c8ed24))
* **blackbox:** implement atomic_store with CAS sharding ([cfa46dd](https://github.com/pproenca/dot-claude/commit/cfa46dd09bd9c8903c11b431d1eb229efc37a74f))
* **blackbox:** implement fast_hash_mmap with mmap ([b52661c](https://github.com/pproenca/dot-claude/commit/b52661c37227cb5ee630dee0913f94e8476553c1))
* **blackbox:** implement main hook logic ([15279d4](https://github.com/pproenca/dot-claude/commit/15279d4ba91b643b3cdd19c5460a2eb77e9fd7c5))
* implement analyze_branch script in Python ([41c894d](https://github.com/pproenca/dot-claude/commit/41c894ded7da4b355227a7fe5d20aafdf51e953a))
* implement posttooluse_validate hook in Python ([dc493e0](https://github.com/pproenca/dot-claude/commit/dc493e0d7048128a23e006ea64fdb8a885aafab8))
* implement pretooluse_safety hook in Python ([e08ce3f](https://github.com/pproenca/dot-claude/commit/e08ce3f6b56282b16d9511d6b122993e560f1c88))
* implement session_start hook in Python ([d673eba](https://github.com/pproenca/dot-claude/commit/d673eba49a1dbae2eaabcfa9159ae5e81eca9ab7))
* **statusline:** add duration and lines changed metrics ([7e89142](https://github.com/pproenca/dot-claude/commit/7e89142d9fb9a7099da9f0e558b38073b987ddf6))
* **super:** add /context and /notes commands ([8985461](https://github.com/pproenca/dot-claude/commit/8985461529e8905c64bcc9ec0182cf62ee5f9230))
* **super:** add worktree-guard hook for main branch warning ([adae3e5](https://github.com/pproenca/dot-claude/commit/adae3e5e2108798eec74b8050a4757469fd1f925))
* update hooks.json to use Python scripts ([e6659b0](https://github.com/pproenca/dot-claude/commit/e6659b01eb5ee909d625b53d31441d3dbcd2f91e))


### Bug Fixes

* **commit:** validate printf pattern for multiline commits ([748b3aa](https://github.com/pproenca/dot-claude/commit/748b3aa1229578d8b9318c2021482991202d242f))
* **dev:** address code review feedback for performance skill ([754f911](https://github.com/pproenca/dot-claude/commit/754f911f33984bf7ef725dc4a419043b852f7dfd))


### Code Refactoring

* **blackbox:** improve code style and add lazy imports ([45ec778](https://github.com/pproenca/dot-claude/commit/45ec7780fec9da0dd99aa4f40b16dc724a7b06c4))
* **commit:** simplify agent and command docs ([1efbe84](https://github.com/pproenca/dot-claude/commit/1efbe8496d53a00664f5828b06bb351f66abb304))
* **dev:** apply Guido & Sam commenting rules to Python skills ([1022b76](https://github.com/pproenca/dot-claude/commit/1022b76502d45ae2d44c8abf392d33f972006e58))
* **dev:** apply progressive disclosure to async-python-patterns ([7c0e4ae](https://github.com/pproenca/dot-claude/commit/7c0e4aed81ee0f176bd9c6fda1031ff3b59988af))
* **dev:** apply progressive disclosure to python-packaging ([df72df9](https://github.com/pproenca/dot-claude/commit/df72df97e67b43bd80b009a424883b7dbd841760))
* **dev:** apply progressive disclosure to python-performance-optimization ([23fc0e7](https://github.com/pproenca/dot-claude/commit/23fc0e7bfd89d6ced08382f93826c0dd70698e39))
* **dev:** apply progressive disclosure to python-testing-patterns ([ad40617](https://github.com/pproenca/dot-claude/commit/ad4061791efa83905e719b9d671dd3a0b6ca1178))
* **dev:** apply progressive disclosure to uv-package-manager ([a3acb89](https://github.com/pproenca/dot-claude/commit/a3acb89f34a3d9fca846070ea725d177ae3ee7f4))
* **dev:** trim python-performance-optimization to under 500 lines ([0410c16](https://github.com/pproenca/dot-claude/commit/0410c1656fc1305193a949db1970c2e435f02951))
* migrate commit plugin from Google style to Conventional Commits ([dcde48a](https://github.com/pproenca/dot-claude/commit/dcde48ab320ff14071130187b6a26ca828c4a124))
* **shell:** use here-strings and parallel analysis ([bb5560f](https://github.com/pproenca/dot-claude/commit/bb5560fa77e523974790a89a240a01325c79aef5))


### Documentation

* add CI/CD documentation for GitHub App ([f1c6d98](https://github.com/pproenca/dot-claude/commit/f1c6d9825901d1dc9c5225563a5c2a230011e481))
* add CLAUDE.md project instructions and remove completed skill-review plan ([7b83f86](https://github.com/pproenca/dot-claude/commit/7b83f86056c57147d4a5e7e64c1a724ed07fc75a))
* add implementation plans for upcoming features ([00ca372](https://github.com/pproenca/dot-claude/commit/00ca37217d72e5c8a857a299d3bf2ddf825753d3))
* **commit:** simplify /commit:new command workflow ([7018b7b](https://github.com/pproenca/dot-claude/commit/7018b7b35d6ee933e2c28a0521eaab04cd6b07b8))
* **plans:** add blackbox read and commit migration plans, remove obsolete plans ([9904e13](https://github.com/pproenca/dot-claude/commit/9904e13efb9adf5b28d4c621cf4d436ed2b0cbec))
* **super:** add integration sections and allowed-tools to skills ([47ed5ce](https://github.com/pproenca/dot-claude/commit/47ed5ceee393975e1522eb84e206247dcfb5612d))
* **sync:** add chmod +x note for statusline.sh ([5813c2c](https://github.com/pproenca/dot-claude/commit/5813c2c313a92fa83138ea25ae146f098da20704))
* update CI-CD.md for GITHUB_TOKEN auth ([38044da](https://github.com/pproenca/dot-claude/commit/38044da03f3544cb3da06b62dadaedb6ee1b164c))
* update commit-organizer to use Python analyze_branch ([d11841e](https://github.com/pproenca/dot-claude/commit/d11841e543d360ab462c3c1736cca539fc4f1c11))
