# Changelog

## [3.1.0](https://github.com/pproenca/dot-claude/compare/v3.0.0...v3.1.0) (2025-12-01)


### Features

* **super:** add Context7 MCP integration to writing-plans skill ([0ee4626](https://github.com/pproenca/dot-claude/commit/0ee4626c6db33946ad66a7375f411e09733dabe4))

## [3.0.0](https://github.com/pproenca/dot-claude/compare/v2.0.0...v3.0.0) (2025-12-01)


### ⚠ BREAKING CHANGES

* **dev:** Plugin namespace changes from dev: to python:
    - dev:python-pro → python:python-expert
    - /dev:scaffold removed
    - /python:refactor added (mirrors shell:refactor pattern)
    - All dev:* skill references → python:*

### Features

* add project-level architect and config-reviewer agents ([71f6dc4](https://github.com/pproenca/dot-claude/commit/71f6dc491547bb542266280b27ea66afa58150c7))
* **agents:** add plugin-automation-analyzer agent ([45d2a5a](https://github.com/pproenca/dot-claude/commit/45d2a5aa2352f21c6d110d9afdfed2abad4cd1e1))
* **dev:** enhance python-pro agent with modern Python patterns ([9add4f1](https://github.com/pproenca/dot-claude/commit/9add4f13169b17a454766b52109e9f91cc01b876))
* **scripts:** add marketplace plugin metadata sync ([ae34371](https://github.com/pproenca/dot-claude/commit/ae34371a033b1afdacdba1dd6c90dcff9591142a))
* **scripts:** add release-please-config consistency check ([e3f53fa](https://github.com/pproenca/dot-claude/commit/e3f53fa8ac1877c1d5579d1bce21df165330ccf5))


### Bug Fixes

* handle missing keys in config update and null sources in plugin validation ([3367774](https://github.com/pproenca/dot-claude/commit/336777427f5e14757bb9468b59534ac5091444b9))
* **scripts:** update release-please config for marketplace structure ([24949f1](https://github.com/pproenca/dot-claude/commit/24949f1d2c099e627adad102d598dd3546f9e9ce))
* **super:** remove tdd-guard hook ([59b0929](https://github.com/pproenca/dot-claude/commit/59b09295456a27a32fb53e79eb110bc8715580e8))
* **super:** standardize skill cross-references and update agent invocations ([51bfc16](https://github.com/pproenca/dot-claude/commit/51bfc160676c794caf081eb1a8b01242a8ea7d62))


### Code Refactoring

* **agents:** remove agent- prefix from dotclaude agents ([c6adf35](https://github.com/pproenca/dot-claude/commit/c6adf355a4604fab7d7d4b7b0c94ea46480dac23))
* **dev:** rename dev plugin to python ([ea239c9](https://github.com/pproenca/dot-claude/commit/ea239c92d3eeb13af7a2c985cf7055ba9b7305e3))
* **scripts:** rewrite validation scripts in Python ([571ed05](https://github.com/pproenca/dot-claude/commit/571ed052b528476c3a5df717245e94dc6ca68183))
* **super:** remove sharing-skills skill ([abce32f](https://github.com/pproenca/dot-claude/commit/abce32f8ed2b297f1d54734e2f435ffe806a24fa))
* **super:** slim down code-reviewer, security-reviewer, diagram-generator agents ([469782d](https://github.com/pproenca/dot-claude/commit/469782d2d5579d4f075b0ad0226de420d3866038))


### Documentation

* add super plugin quality improvement plans ([37f17f4](https://github.com/pproenca/dot-claude/commit/37f17f4b0f9c93d24ef3e52d114b1c4e1f85e14e))
* **commit:** remove backticks from inline punctuation markers ([05b0a5b](https://github.com/pproenca/dot-claude/commit/05b0a5bb32d8ac1d2f66fb9b963639ca96159f64))
* **init:** update claude to use 'uv' for python ([0db55a7](https://github.com/pproenca/dot-claude/commit/0db55a79b2f2c55a767765ca868781ab7aa8a027))
* **super:** add code-review-standards reference ([b81961c](https://github.com/pproenca/dot-claude/commit/b81961cc4e3ca0ab07feb69e498f684c8573527e))

## [2.0.0](https://github.com/pproenca/dot-claude/compare/v1.0.1...v2.0.0) (2025-11-30)


### ⚠ BREAKING CHANGES

* **plugins:** Removes context-manager agent, /agent:improve and
* Plugin paths have changed from nested structure to flat organization under plugins/.

### Features

* **agent:** add multi-agent orchestration plugin ([a59c663](https://github.com/pproenca/dot-claude/commit/a59c663f0ae81e5a3dce106c01173cc6b2ca701a))
* **analyze:** add marketplace analysis plugin ([912bd6a](https://github.com/pproenca/dot-claude/commit/912bd6a57c0e64b8d9f4d345e4a1eba6a89d1381))
* **blackbox:** add flight recorder plugin with file snapshot recovery ([130d75c](https://github.com/pproenca/dot-claude/commit/130d75c51f5b17a26f72a62629ca686f355df55a))
* **blackbox:** add flight recorder telemetry plugin ([a1683f1](https://github.com/pproenca/dot-claude/commit/a1683f11b54a8189a1598e58d8b2cc3d0beeea12))
* **commit:** add git workflow plugin with Python hooks ([dcf5151](https://github.com/pproenca/dot-claude/commit/dcf5151b66a43517584f5061024aeed566b1811f))
* **debug:** add distributed systems debugging plugin ([282e720](https://github.com/pproenca/dot-claude/commit/282e720cb6401aa9c56886efaa34a38fad9cc427))
* **dev:** add Python development skills with progressive disclosure ([f3217a3](https://github.com/pproenca/dot-claude/commit/f3217a39dd3554703aac70f6a1d29d0e8e5b5c8b))
* **doc:** add documentation skills with Amazon writing style ([fcacae5](https://github.com/pproenca/dot-claude/commit/fcacae56ec917004a064b50deddff84998971c11))
* **shell:** add shell scripting plugin with Google Style Guide ([b0f970d](https://github.com/pproenca/dot-claude/commit/b0f970dd39dc15c0a1951f6540448a168a8e50ae))
* **statusline:** add duration and lines changed metrics ([537f004](https://github.com/pproenca/dot-claude/commit/537f004298bd0c103dbbb15f592d993c9e72ee8f))
* **super:** add core workflow skills and hooks ([7ccb820](https://github.com/pproenca/dot-claude/commit/7ccb820f0bc64379314faace5b034bc5df1e84bd))


### Bug Fixes

* **commit:** scope hook matchers to git commands only ([a5d7cbb](https://github.com/pproenca/dot-claude/commit/a5d7cbbfdf901358650b7389ae0f4e4d0d8f9295))
* **plugins:** address quality issues from marketplace analysis ([5db763e](https://github.com/pproenca/dot-claude/commit/5db763e4e39e90ef96a7a4ad494046878873c9b2))


### Code Refactoring

* **debug:** split trace.md command into core + references ([72af5e6](https://github.com/pproenca/dot-claude/commit/72af5e66391d1d45042ee1aa1ef8828be7161055))
* **dev:** consolidate agents and add workflow integration ([2a101bd](https://github.com/pproenca/dot-claude/commit/2a101bd0a0ab2164d585b75675dc9f93022df7b5))
* flatten plugin directory structure ([0fe29d2](https://github.com/pproenca/dot-claude/commit/0fe29d28e3695056c952d3d2841d0bf3ca49c61d))
* **plugins:** remove agent plugin ([8d3ca08](https://github.com/pproenca/dot-claude/commit/8d3ca086b71174ec7e6099a92bb40c8d31076040))
* **plugins:** remove agent plugin references from documentation ([089eef6](https://github.com/pproenca/dot-claude/commit/089eef6891563dac8fd9f329165f25f754d10966))
* **shell:** simplify shell plugin and add verification requirements ([00a2eac](https://github.com/pproenca/dot-claude/commit/00a2eac67232f84d317c5f38ede917d5e1a03f3e))
* **tdd-guard:** switch to whitelist approach for code file detection ([35a0623](https://github.com/pproenca/dot-claude/commit/35a0623bb532dcd4648f85e0b0e0d6bc76704a56))


### Documentation

* add implementation plans for development reference ([7a861bb](https://github.com/pproenca/dot-claude/commit/7a861bb410f1378b62c07ab1f2a61b7eee9cfb56))
* add README and CLAUDE.md project documentation ([afd52ee](https://github.com/pproenca/dot-claude/commit/afd52ee9a52e0941bd25769833256692a62310c0))
* add usage examples to agent definitions ([b75fabd](https://github.com/pproenca/dot-claude/commit/b75fabdf7bc296f86146c13296698da7b8765806))
* **analyze:** add reference documentation for marketplace-analysis skill ([8c19325](https://github.com/pproenca/dot-claude/commit/8c1932598998999cf5077c3477386f0f659755ff))

## [1.0.1](https://github.com/pproenca/dot-claude/compare/v1.0.0...v1.0.1) (2025-11-30)


### Documentation

* add usage examples to agent definitions ([8399cb3](https://github.com/pproenca/dot-claude/commit/8399cb35bc6ee467e27dc9e843895a5e213283eb))
