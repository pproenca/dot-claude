# Changelog

## [1.0.0](https://github.com/pproenca/dot-claude/compare/v1.0.0...v1.0.0) (2025-12-03)


### ⚠ BREAKING CHANGES

* super plugin removed. Use core, workflow, review, testing, meta, debug plugins instead.
* Super plugin is now deprecated. Use new focused plugins:
    - core: TDD, verification, brainstorming (essential capabilities)
    - workflow: writing-plans, executing-plans, subagent-dev, git-worktrees
    - review: code-review (merged requesting + receiving)
    - testing: anti-patterns, condition-wait
    - meta: writing-skills, testing-skills, marketplace-analysis
    - debug: systematic, root-cause, defense-in-depth (from Phase 3)
* **dev:** Plugin namespace changes from dev: to python:
    - dev:python-pro → python:python-expert
    - /dev:scaffold removed
    - /python:refactor added (mirrors shell:refactor pattern)
    - All dev:* skill references → python:*
* **plugins:** Removes context-manager agent, /agent:improve and
* Plugin paths have changed from nested structure to flat organization under plugins/.

### Features

* add explicit TDD and verification skill requirements to workflow ([73b1af2](https://github.com/pproenca/dot-claude/commit/73b1af2b794fcd589f4ca986bbc0493277b9c2fb))
* add project-level architect and config-reviewer agents ([ea6daa0](https://github.com/pproenca/dot-claude/commit/ea6daa0c988d14e0d604006a971de3f66b8b83b3))
* add settings and plugin validation tooling ([e3ace13](https://github.com/pproenca/dot-claude/commit/e3ace1359bc9b7e549021b457810544e539fc072))
* **agent:** add multi-agent orchestration plugin ([de7f875](https://github.com/pproenca/dot-claude/commit/de7f87501384ad6789ceadb9d5f6cd7675267ccf))
* **agents:** add plugin-automation-analyzer agent ([06cd79b](https://github.com/pproenca/dot-claude/commit/06cd79b00c1e0b821a5a14d37c32079d13725991))
* **analyze:** add marketplace analysis plugin ([1f1fb1c](https://github.com/pproenca/dot-claude/commit/1f1fb1c4b73290d67563dbb9b0e5346cb65dbc26))
* **blackbox:** add flight recorder plugin with file snapshot recovery ([497bfa7](https://github.com/pproenca/dot-claude/commit/497bfa7a2017fc7e63e91ed094c7c22c07cb176f))
* **blackbox:** add flight recorder telemetry plugin ([71c96a0](https://github.com/pproenca/dot-claude/commit/71c96a01fcaacc1fdd703dce904e450addadac50))
* **commit:** add git workflow plugin with Python hooks ([280d584](https://github.com/pproenca/dot-claude/commit/280d5845668f2cb5633d24ffd5443afc0ffe372b))
* **debug:** add distributed systems debugging plugin ([3d11404](https://github.com/pproenca/dot-claude/commit/3d1140451a5acf5567393d804755eb519e330a75))
* **dev:** add Python development skills with progressive disclosure ([2b3f395](https://github.com/pproenca/dot-claude/commit/2b3f3957e52e104fba003309041d6dd03ad3178d))
* **dev:** enhance python-pro agent with modern Python patterns ([e8227be](https://github.com/pproenca/dot-claude/commit/e8227be5d8f35de99ff7739371372e5abd54c717))
* **doc:** add commands to integrate orphaned doc agents ([ab5f7e3](https://github.com/pproenca/dot-claude/commit/ab5f7e35bbe681f3a1f842e07c1d45ba57946ab5))
* **doc:** add documentation skills with Amazon writing style ([672f217](https://github.com/pproenca/dot-claude/commit/672f217d006b492f6c5e3b09b602ab966dc762fd))
* **doc:** move diagram-generator agent from super ([113dd45](https://github.com/pproenca/dot-claude/commit/113dd45d98ac6d44cad50df752816e7aae370c78))
* **review:** move code-review-standards reference from super ([0662d4a](https://github.com/pproenca/dot-claude/commit/0662d4a4185edaaf92117f12f6c19948e7ccfcba))
* **review:** move security-reviewer agent from super ([ffc1d2f](https://github.com/pproenca/dot-claude/commit/ffc1d2f361abd90cd18a13efdb0a58dfc9ccc4a9))
* **scripts:** add marketplace plugin metadata sync ([8093453](https://github.com/pproenca/dot-claude/commit/80934535b22461f148c5ce08788b6603aa5b7501))
* **scripts:** add release-please-config consistency check ([70a6d46](https://github.com/pproenca/dot-claude/commit/70a6d46f872bff315a522e368073c3bdbeccb4fb))
* **shell:** add shell scripting plugin with Google Style Guide ([ce584ed](https://github.com/pproenca/dot-claude/commit/ce584edb51eae0312aae37f15dc957e158dc18ef))
* split super plugin into focused modules (Phase 4) ([384ee68](https://github.com/pproenca/dot-claude/commit/384ee68cef4e0851cba26719be304af1932c46c3))
* **statusline:** add duration and lines changed metrics ([007eeca](https://github.com/pproenca/dot-claude/commit/007eecac34b315376fc3ac58a6de796bef329f93))
* **super:** add Context7 MCP integration to writing-plans skill ([b9f612b](https://github.com/pproenca/dot-claude/commit/b9f612bb5458a7de836775fac7ace8fba0f9fce6))
* **super:** add core workflow skills and hooks ([91c58dc](https://github.com/pproenca/dot-claude/commit/91c58dca162dd4dccca6f0ba4095ed74203c6466))
* **workflow:** improve diagram generation with auto-detect mode ([fcbea1c](https://github.com/pproenca/dot-claude/commit/fcbea1c607ee3ec7e7952cf4cff435d7003221f4))
* **workflow:** move slash commands from super ([ae593b1](https://github.com/pproenca/dot-claude/commit/ae593b1221da5c412aaff05c5e694fda469659bc))
* **workflow:** move worktree-guard hook from super ([cc040b5](https://github.com/pproenca/dot-claude/commit/cc040b5bb2cd807a0ac913fa3a387e374496dad4))
* **workflow:** restore lost code review templates and add reference validation ([cfd367c](https://github.com/pproenca/dot-claude/commit/cfd367c27bb880209bec59da73c1f6225cd0d979))


### Bug Fixes

* add worktree isolation check to subagent-dev skill ([e57a63b](https://github.com/pproenca/dot-claude/commit/e57a63b3a505abfd292d4cd578dc22cf51bd936d))
* address PR review comments for namespace prefixes and code quality ([123715c](https://github.com/pproenca/dot-claude/commit/123715ccf9c1895dc3a489570b41a55c16b417ea))
* address PR review comments for skill references and branding ([d7a216f](https://github.com/pproenca/dot-claude/commit/d7a216f7ac2da7009a0cc3d63a8a7739ef260f86))
* **analyze:** add namespace prefix to agent invocations and reference validation ([2d61afe](https://github.com/pproenca/dot-claude/commit/2d61afef271d96f3b92280838d23e6b2c4e945be))
* **commit:** scope hook matchers to git commands only ([d7207ea](https://github.com/pproenca/dot-claude/commit/d7207eabb1e0c44bd477411a19526075a90e8afa))
* **doc:** condense diagram-generator agent to meet size limit ([4b9f0f7](https://github.com/pproenca/dot-claude/commit/4b9f0f7685b401550946b5bba059a9ca3b04ccd3))
* **doc:** correct skill-vs-agent confusion in diagram-generator ([cd4068a](https://github.com/pproenca/dot-claude/commit/cd4068a88cdd74f485204d297adbdfb117df7438))
* enforce AskUserQuestion tool usage in skills ([4874ba3](https://github.com/pproenca/dot-claude/commit/4874ba3b2f4cac0ef8be71dd227a356f637b8ad3))
* enforce finish-branch invocation via mandatory TodoWrite tracking ([24c727e](https://github.com/pproenca/dot-claude/commit/24c727eb6573e82c758c1dac3a9223c7f9c31d5e))
* handle missing keys in config update and null sources in plugin validation ([e57b170](https://github.com/pproenca/dot-claude/commit/e57b1700a547e9ef7b61e2dcdc5fbbd1987ea728))
* **plugins:** address quality issues from marketplace analysis ([6751091](https://github.com/pproenca/dot-claude/commit/675109103358670307029520d6f797056374f47b))
* **scripts:** update release-please config for marketplace structure ([5087ca7](https://github.com/pproenca/dot-claude/commit/5087ca71e89ee5c922e397e277de2b2b05fdf0a0))
* **super:** remove tdd-guard hook ([35b9766](https://github.com/pproenca/dot-claude/commit/35b9766a12a080eb97b992b0151e5f3b1b2cd274))
* **super:** standardize skill cross-references and update agent invocations ([97cf852](https://github.com/pproenca/dot-claude/commit/97cf852290b33d09b05d56949d70a781324ca14f))
* validate bare plugin names in Skill patterns ([8d6f174](https://github.com/pproenca/dot-claude/commit/8d6f17464683d9bf90ba96e59c9f242018a3407d))
* **workflow:** use AskUserQuestion for execution handoff ([cf781e8](https://github.com/pproenca/dot-claude/commit/cf781e8caadf3abcda924eede9589d485ad0db15))


### Code Refactoring

* **agents:** remove agent- prefix from dotclaude agents ([ff3a527](https://github.com/pproenca/dot-claude/commit/ff3a527814f4366787e4a8c4a501582eddf8452c))
* **debug:** split trace.md command into core + references ([e3310d1](https://github.com/pproenca/dot-claude/commit/e3310d17cf4e503a9c7f595a1720d5be22e8a6a2))
* **debug:** trim devops-troubleshooter agent ([6e91078](https://github.com/pproenca/dot-claude/commit/6e910787056003a5a812d66f4912af645e5ba4d2))
* **dev:** consolidate agents and add workflow integration ([72a8a19](https://github.com/pproenca/dot-claude/commit/72a8a196d47cecc1b6c093c04e503b0af5ec569f))
* **dev:** rename dev plugin to python ([b2c6b67](https://github.com/pproenca/dot-claude/commit/b2c6b67eae6eee9cfc3500188b6dc75c91caf21e))
* **doc:** extract mermaid syntax to reference file ([00c138a](https://github.com/pproenca/dot-claude/commit/00c138ac9c99e80d8b8d13233f35a97d51036b4f))
* flatten plugin directory structure ([8ab801c](https://github.com/pproenca/dot-claude/commit/8ab801c4fbefee532cc2d246a01f9901a5b3412f))
* merge analyze plugin into meta and fix deprecated references ([e929178](https://github.com/pproenca/dot-claude/commit/e9291782c5bf8de9f44656f7025ce24fcae27a42))
* **plugins:** remove agent plugin ([c3c30b9](https://github.com/pproenca/dot-claude/commit/c3c30b92ccb5160620f2db8ff3eeaa3056e0d09e))
* **plugins:** remove agent plugin references from documentation ([d8f6bc6](https://github.com/pproenca/dot-claude/commit/d8f6bc63d1369439caf9eb3ab70dbff2fae92d52))
* remove deprecated super plugin ([1a71ff5](https://github.com/pproenca/dot-claude/commit/1a71ff58c4094acda6745925991d8338464ca054))
* remove unused workflow commands and orphaned blackbox directory ([c72a6be](https://github.com/pproenca/dot-claude/commit/c72a6be4ea49452d4d87b41992ccb533db8e5910))
* reorganize plugins into tier-based structure ([325b92b](https://github.com/pproenca/dot-claude/commit/325b92b3c9719bebb6ac16cfe17d80a6d7845f12))
* **scripts:** rewrite validation scripts in Python ([240bc3f](https://github.com/pproenca/dot-claude/commit/240bc3f59e6dc116ddb2764bb7c70bfde4454f6a))
* **shell:** simplify shell plugin and add verification requirements ([87e3d0f](https://github.com/pproenca/dot-claude/commit/87e3d0f3bb2a4ace27e3e078f07479f4115caffc))
* **super:** remove sharing-skills skill ([cac5f46](https://github.com/pproenca/dot-claude/commit/cac5f46bbb7d79dc6d6331da671983c6f81478a7))
* **super:** rename verbose skill names to be concise ([71f3e46](https://github.com/pproenca/dot-claude/commit/71f3e4685ca59ef62b30c41c6a24383b7324157e))
* **super:** simplify diagram-generator to delegate to mermaid-expert ([67e0a9a](https://github.com/pproenca/dot-claude/commit/67e0a9a4ca4cd107a96707232e88d5d7338665c5))
* **super:** slim down code-reviewer, security-reviewer, diagram-generator agents ([0b498eb](https://github.com/pproenca/dot-claude/commit/0b498eb5d1e5d3715751682f72d8df4f0443570d))
* **super:** update TDD and testing skills, remove completed plans ([6b7e72e](https://github.com/pproenca/dot-claude/commit/6b7e72e64a872c05a530aa1cd47bd37465f5c287))
* **tdd-guard:** switch to whitelist approach for code file detection ([f17f759](https://github.com/pproenca/dot-claude/commit/f17f759bac06e48bc2abe17b01f7df2bfa585cb8))
* update all super:* references to new plugin names ([ede2c8f](https://github.com/pproenca/dot-claude/commit/ede2c8fbc4080570380f4983cd842220edf414b2))
* update cross-references and description patterns ([75b614b](https://github.com/pproenca/dot-claude/commit/75b614b941e3aa7382e68a7d99389ea1bca8a3cb))


### Documentation

* add implementation plan for super plugin removal ([208391c](https://github.com/pproenca/dot-claude/commit/208391cdecee3a8f74dc392e6b221b028616053d))
* add implementation plans for development reference ([3786dac](https://github.com/pproenca/dot-claude/commit/3786dac2fb01ca4ac2b4eb17652d0385d6d8e2dd))
* add migration guide and supporting files ([54dc0b9](https://github.com/pproenca/dot-claude/commit/54dc0b95ad03bf83422068e50d3a63aa131c3213))
* add README and CLAUDE.md project documentation ([a86dc7d](https://github.com/pproenca/dot-claude/commit/a86dc7da6238d0aedd246acd69af57ed8812a0e3))
* add super plugin quality improvement plans ([3c7ef19](https://github.com/pproenca/dot-claude/commit/3c7ef19698588c00441a5585405a3d7611ba6902))
* add usage examples to agent definitions ([35cfccf](https://github.com/pproenca/dot-claude/commit/35cfccf27dfa34ffd5263adf660165110f30f841))
* **analyze:** add reference documentation for marketplace-analysis skill ([096ae36](https://github.com/pproenca/dot-claude/commit/096ae364b01b0634cd4912ae791f8ded00c6faa4))
* **commit:** remove backticks from inline punctuation markers ([0cbef01](https://github.com/pproenca/dot-claude/commit/0cbef011228a970803b2fa073bfd3488c4e6f6e9))
* fix stale skill names and remove non-existent Cursor section ([01b2b4a](https://github.com/pproenca/dot-claude/commit/01b2b4a5b2d1b0921c9fb7dfe02958895d06a3df))
* **init:** update claude to use 'uv' for python ([a4e2818](https://github.com/pproenca/dot-claude/commit/a4e2818d122136ca3899675f170946c7b2739d80))
* mark migration complete in MIGRATION.md ([0613b13](https://github.com/pproenca/dot-claude/commit/0613b13a482aa5b92a3cdf8227e6f432237195fb))
* **python:** add fallback text for graceful degradation (Phase 5) ([0d9f2c7](https://github.com/pproenca/dot-claude/commit/0d9f2c7cb74bfda36da318354eda282c760dc0b3))
* **python:** update skills and agent to use uv consistently ([4e694be](https://github.com/pproenca/dot-claude/commit/4e694be56f45dc24626e58c4d2c27886766e202e))
* remove deprecated plan ([3b95f01](https://github.com/pproenca/dot-claude/commit/3b95f01ee35a5808d1e00018089ae6a20de74759))
* remove super plugin from CLAUDE.md ([deabb3e](https://github.com/pproenca/dot-claude/commit/deabb3e64994d730bcfe9c0f114a657bb97f534a))
* **super:** add code-review-standards reference ([52facc6](https://github.com/pproenca/dot-claude/commit/52facc6a771473e3004bbe481d7de64c5d0c43b0))
* update CLAUDE.md for new plugin architecture (Phase 6) ([410caae](https://github.com/pproenca/dot-claude/commit/410caaee01ed1508b84d2a54ea81b9c920b132d0))
* update instructions to use uv consistently ([335aa19](https://github.com/pproenca/dot-claude/commit/335aa19991de02c4317c74ed00ac6a4ae471bdee))
* update README for super plugin removal ([7f92c6f](https://github.com/pproenca/dot-claude/commit/7f92c6f5fbea14639a22b963d860c2bd186f7221))
* update structure ([179930b](https://github.com/pproenca/dot-claude/commit/179930b1f27ddf94b9c353119699cdd92c60b237))
* update workflow and doc plugins to use uv ([65fd3c6](https://github.com/pproenca/dot-claude/commit/65fd3c62b4119d50a63aacb76d442a5c9fa310ba))


### Maintenance

* reset versioning to 1.0.0 ([8f77d1e](https://github.com/pproenca/dot-claude/commit/8f77d1ea397c9389646ac046647eb6e8f249f77e))

## Changelog

All notable changes to this project will be documented in this file.
