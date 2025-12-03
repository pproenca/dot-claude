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

* add explicit TDD and verification skill requirements to workflow ([24f6428](https://github.com/pproenca/dot-claude/commit/24f6428c0917f9cee98bb1ace7452a4fe63988e6))
* add project-level architect and config-reviewer agents ([2861abf](https://github.com/pproenca/dot-claude/commit/2861abfbe8e2130ba0e9a87c3a226ceee5135d07))
* add settings and plugin validation tooling ([0e27e45](https://github.com/pproenca/dot-claude/commit/0e27e45a2f03843629eea21a1fea43b81f27aa90))
* **agent:** add multi-agent orchestration plugin ([2a7a417](https://github.com/pproenca/dot-claude/commit/2a7a417f5427b9f6f666f999d63b99b1dbae3163))
* **agents:** add plugin-automation-analyzer agent ([54e30c3](https://github.com/pproenca/dot-claude/commit/54e30c33f59e15aaba286f4e046bb4cc747d1929))
* **analyze:** add marketplace analysis plugin ([f9b56f4](https://github.com/pproenca/dot-claude/commit/f9b56f46606c3a092fc50a3df3f5562a9e1d95b4))
* **blackbox:** add flight recorder plugin with file snapshot recovery ([91362a3](https://github.com/pproenca/dot-claude/commit/91362a345c139dc9ca4031b1c4dc9860b926b370))
* **blackbox:** add flight recorder telemetry plugin ([c0a6cc8](https://github.com/pproenca/dot-claude/commit/c0a6cc80286bcb39474e0aafe695ad12374ce5df))
* **commit:** add git workflow plugin with Python hooks ([86f2c99](https://github.com/pproenca/dot-claude/commit/86f2c997b78f135d23738ebc898b7e2f79fba570))
* **debug:** add distributed systems debugging plugin ([c08247a](https://github.com/pproenca/dot-claude/commit/c08247a1ad8b401d86e711163dd558387e4a92a0))
* **dev:** add Python development skills with progressive disclosure ([f8e61cc](https://github.com/pproenca/dot-claude/commit/f8e61ccb821045f54ba15de7ecdae1f8cc02dfdb))
* **dev:** enhance python-pro agent with modern Python patterns ([8173b80](https://github.com/pproenca/dot-claude/commit/8173b80476af43feb2f27071b0862d04aceafbb3))
* **doc:** add commands to integrate orphaned doc agents ([f2f3a0c](https://github.com/pproenca/dot-claude/commit/f2f3a0cd93a5a78bd13aea04376c0bcae7c93552))
* **doc:** add documentation skills with Amazon writing style ([1eb9c52](https://github.com/pproenca/dot-claude/commit/1eb9c52eba21c3104dc674c4ab2062685c3d31ef))
* **doc:** move diagram-generator agent from super ([1d946b9](https://github.com/pproenca/dot-claude/commit/1d946b97eafaa1b689b7ef58b3cd1712d4dc00a1))
* **python:** add decision-based commenting philosophy ([b07b514](https://github.com/pproenca/dot-claude/commit/b07b514af2d0c1a5497980d71409d757f1c33716))
* **python:** add specialized framework agents and django styleguide ([3a32662](https://github.com/pproenca/dot-claude/commit/3a32662672facac73a52393f424781cf2526e4f2))
* **review:** move code-review-standards reference from super ([5099a00](https://github.com/pproenca/dot-claude/commit/5099a00d499525fbbe341ce82dbdb18ea80ec35e))
* **review:** move security-reviewer agent from super ([1420c4a](https://github.com/pproenca/dot-claude/commit/1420c4aa44434ee9e242dc559c06f8c477d24737))
* **scripts:** add marketplace plugin metadata sync ([02b1e47](https://github.com/pproenca/dot-claude/commit/02b1e47c49106b754325dbf59c1b84c83b1fa66d))
* **scripts:** add release-please-config consistency check ([a043ebb](https://github.com/pproenca/dot-claude/commit/a043ebb223f151bb450a986e544a49299fe77136))
* **shell:** add shell scripting plugin with Google Style Guide ([2fc7e1b](https://github.com/pproenca/dot-claude/commit/2fc7e1b7d61c17f39186a5a428cad8d4a7f3954f))
* split super plugin into focused modules (Phase 4) ([3edb2d1](https://github.com/pproenca/dot-claude/commit/3edb2d173166269b3da2d1a9d1ec5db5951d65bc))
* **statusline:** add duration and lines changed metrics ([82e0951](https://github.com/pproenca/dot-claude/commit/82e0951501df2f6277498e12a90a5c51d1821c14))
* **super:** add Context7 MCP integration to writing-plans skill ([daec65c](https://github.com/pproenca/dot-claude/commit/daec65c35cf97a3e15736865cbba639fb071a643))
* **super:** add core workflow skills and hooks ([717e5ef](https://github.com/pproenca/dot-claude/commit/717e5ef519b4197e8d3c23a122ec45d3eb376587))
* **workflow:** add complexity-aware subagent dispatch with efficiency targets ([2b0908a](https://github.com/pproenca/dot-claude/commit/2b0908a9d57bf37e0daf699efd75eb69ead6eec4))
* **workflow:** add complexity-aware task execution to executing-plans ([4da0666](https://github.com/pproenca/dot-claude/commit/4da0666fb68db078e812ad408e54e77f410ed6f7))
* **workflow:** add task complexity classification to writing-plans ([1e6a9e5](https://github.com/pproenca/dot-claude/commit/1e6a9e564a3f4a2c32b10a7dbb666dcbae947902))
* **workflow:** improve diagram generation with auto-detect mode ([e9c775e](https://github.com/pproenca/dot-claude/commit/e9c775ef06602fdff8d1d40ee9bee84a897ec353))
* **workflow:** move slash commands from super ([53ee4f8](https://github.com/pproenca/dot-claude/commit/53ee4f885d4048cca510711fe3c961a64f9dc133))
* **workflow:** move worktree-guard hook from super ([2a6875a](https://github.com/pproenca/dot-claude/commit/2a6875a038ab21683dcce4be373e99c0660e3d40))
* **workflow:** restore lost code review templates and add reference validation ([2381e1e](https://github.com/pproenca/dot-claude/commit/2381e1e4e44398b5c3738dc64bdbe1cd6b0f9c82))


### Bug Fixes

* add MCP tool pattern support to settings validation ([3791c27](https://github.com/pproenca/dot-claude/commit/3791c274a986123005bf746d18a87d390bcbf85b))
* add safe worktree cleanup sequence to finish-branch skill ([999a33a](https://github.com/pproenca/dot-claude/commit/999a33aa5662bf2b62b42b893c9a95df6cb709cd))
* add ty override for plugin tests with dynamic imports ([0ca03ec](https://github.com/pproenca/dot-claude/commit/0ca03ec86d52a876dea88002c5d3275f3cd27627))
* add worktree isolation check to subagent-dev skill ([a4b9002](https://github.com/pproenca/dot-claude/commit/a4b900286dc5963366ff3113ffe75553b388cf74))
* address PR review comments for namespace prefixes and code quality ([b00b34c](https://github.com/pproenca/dot-claude/commit/b00b34c72cb4af6b93d0d27535a0923b402d48ce))
* address PR review comments for skill references and branding ([08c1f54](https://github.com/pproenca/dot-claude/commit/08c1f5458b3cb05e556bb0942dc3ff40fd02c150))
* **analyze:** add namespace prefix to agent invocations and reference validation ([21d8297](https://github.com/pproenca/dot-claude/commit/21d8297e10565bb076b571c055fbc096958e7eda))
* **commit:** scope hook matchers to git commands only ([002ba83](https://github.com/pproenca/dot-claude/commit/002ba8307b4675d141de35e143f8d8aa4d5684df))
* **doc:** condense diagram-generator agent to meet size limit ([17e5468](https://github.com/pproenca/dot-claude/commit/17e5468abdf78a5428a39eed33ad275dc8b29150))
* **doc:** correct skill-vs-agent confusion in diagram-generator ([d414902](https://github.com/pproenca/dot-claude/commit/d4149024315cb4c55dd5301ba7095fa3f16c4f51))
* enforce AskUserQuestion tool usage in skills ([ff85b08](https://github.com/pproenca/dot-claude/commit/ff85b08fb1e173bc5d76e3a650517ff6a2ab6a81))
* enforce finish-branch invocation via mandatory TodoWrite tracking ([829f00b](https://github.com/pproenca/dot-claude/commit/829f00bbbf36737e1df9a197bb5f18c057a2e8da))
* handle missing keys in config update and null sources in plugin validation ([025afdf](https://github.com/pproenca/dot-claude/commit/025afdf5b449ec302065a12dbc035b80151dc68f))
* **plugins:** address quality issues from marketplace analysis ([6c493dc](https://github.com/pproenca/dot-claude/commit/6c493dcab20be5309a2ea6c0be611d2606255518))
* **scripts:** update release-please config for marketplace structure ([4cd77a3](https://github.com/pproenca/dot-claude/commit/4cd77a38fd3235f76176a2574c95e99c194f8d68))
* **super:** remove tdd-guard hook ([054a33d](https://github.com/pproenca/dot-claude/commit/054a33d48538eeedfc20e9d8411d6f9338c877e0))
* **super:** standardize skill cross-references and update agent invocations ([3988d9c](https://github.com/pproenca/dot-claude/commit/3988d9c8f6f637c3f0eaf64be18ef90ce5fac598))
* validate bare plugin names in Skill patterns ([31acbb8](https://github.com/pproenca/dot-claude/commit/31acbb853af34d0f890edddebc1c5a0efcc3b761))
* **workflow:** use AskUserQuestion for execution handoff ([4bfb9f7](https://github.com/pproenca/dot-claude/commit/4bfb9f7a2329d11731b8194b9923a8b9c421b95a))


### Code Refactoring

* **agents:** remove agent- prefix from dotclaude agents ([0a7d095](https://github.com/pproenca/dot-claude/commit/0a7d095e84efc2b83569b98aeb455051ef9d4dc6))
* **debug:** split trace.md command into core + references ([2631bad](https://github.com/pproenca/dot-claude/commit/2631bad18ba11294a7a3dc7be0183de8297fecf1))
* **debug:** trim devops-troubleshooter agent ([d6748ee](https://github.com/pproenca/dot-claude/commit/d6748ee19767f1c350f39d576be917b9be704c65))
* **dev:** consolidate agents and add workflow integration ([7d9e3b3](https://github.com/pproenca/dot-claude/commit/7d9e3b369cd151fb7ddd86b1d180e4b14814bc48))
* **dev:** rename dev plugin to python ([f7951d9](https://github.com/pproenca/dot-claude/commit/f7951d9899725afff53c0a296fe8c9e3dcbbb95f))
* **doc:** extract mermaid syntax to reference file ([1c77421](https://github.com/pproenca/dot-claude/commit/1c774212b77aa9d2d6e5d484fe7d822f14e6ddf0))
* flatten plugin directory structure ([e65189b](https://github.com/pproenca/dot-claude/commit/e65189baf94ecb6a1ba59c9638ad028c2668cab7))
* merge analyze plugin into meta and fix deprecated references ([d6209f4](https://github.com/pproenca/dot-claude/commit/d6209f475f1ea966c845c58aedd5cc426b7a4a17))
* **plugins:** remove agent plugin ([e56a358](https://github.com/pproenca/dot-claude/commit/e56a35806ae15ef7575e7c1d5bf6df8de26d3e96))
* **plugins:** remove agent plugin references from documentation ([7acb2c9](https://github.com/pproenca/dot-claude/commit/7acb2c9277e996e6ecb5b338fa68093e11499b57))
* **python:** consolidate skills with Pythonic style preamble ([f2c018a](https://github.com/pproenca/dot-claude/commit/f2c018aca8618ec71a8646e81a2ab7ca781d67bd))
* remove deprecated super plugin ([06bbfb5](https://github.com/pproenca/dot-claude/commit/06bbfb580efa252e433680cf9ee9cbf9e583dd7e))
* remove unused workflow commands and orphaned blackbox directory ([28dfb24](https://github.com/pproenca/dot-claude/commit/28dfb2441ca05299a7d5e566ebad8fb4644517c7))
* reorganize plugins into tier-based structure ([b55247a](https://github.com/pproenca/dot-claude/commit/b55247ae9a69c164ade78b1b64e5d35ee8b245b2))
* **scripts:** rewrite validation scripts in Python ([9c2a137](https://github.com/pproenca/dot-claude/commit/9c2a13730330eac5692ae3fa3f0ee92dd24c0371))
* **shell:** simplify shell plugin and add verification requirements ([b3a6032](https://github.com/pproenca/dot-claude/commit/b3a6032d398cb2356b0a9dd439dc2b868aa10544))
* **super:** remove sharing-skills skill ([ccba66a](https://github.com/pproenca/dot-claude/commit/ccba66a76914d3ecc91552eb704f86962db6275d))
* **super:** rename verbose skill names to be concise ([6b1e41a](https://github.com/pproenca/dot-claude/commit/6b1e41a00e9799e399f251be1f91bbcc00dd2a30))
* **super:** simplify diagram-generator to delegate to mermaid-expert ([5fed059](https://github.com/pproenca/dot-claude/commit/5fed059b523eb3fa2925653668dd0bfc30569d94))
* **super:** slim down code-reviewer, security-reviewer, diagram-generator agents ([c7d69cd](https://github.com/pproenca/dot-claude/commit/c7d69cd65b430427c8cfcf47bd93570809b8eee4))
* **super:** update TDD and testing skills, remove completed plans ([6e46ba4](https://github.com/pproenca/dot-claude/commit/6e46ba4ec3a47cc41dec47d0e7ae537fceb1af2d))
* **tdd-guard:** switch to whitelist approach for code file detection ([fe839da](https://github.com/pproenca/dot-claude/commit/fe839da787649899ca247dc463df57101a245798))
* update all super:* references to new plugin names ([5965fba](https://github.com/pproenca/dot-claude/commit/5965fba94779f1a954dd19a40fd39c8eb10571db))
* update cross-references and description patterns ([f247904](https://github.com/pproenca/dot-claude/commit/f247904d5e1e9163273e258c29e117ca752c5d41))


### Documentation

* add implementation plan for super plugin removal ([c514bc0](https://github.com/pproenca/dot-claude/commit/c514bc0e7d976bd4296d252cc4979658ef094f53))
* add implementation plans for development reference ([9e43023](https://github.com/pproenca/dot-claude/commit/9e43023e53cdaeddebbcd6df5f9c4b705b209ffa))
* add migration guide and supporting files ([30c0dad](https://github.com/pproenca/dot-claude/commit/30c0dad55f4c828b46cee570cba448ac1f7869b5))
* add README and CLAUDE.md project documentation ([2fc3d27](https://github.com/pproenca/dot-claude/commit/2fc3d273266a8e179d198c6594adc70609ff36bf))
* add super plugin quality improvement plans ([3d1b4c0](https://github.com/pproenca/dot-claude/commit/3d1b4c0ae28032f45215fa8943b2162859be761c))
* add usage examples to agent definitions ([da41b69](https://github.com/pproenca/dot-claude/commit/da41b691ca32dce8a96dea5e2a2ac723d2ce9df7))
* **analyze:** add reference documentation for marketplace-analysis skill ([958476d](https://github.com/pproenca/dot-claude/commit/958476d550795fb6ace304cf50784ac53d489271))
* **commit:** remove backticks from inline punctuation markers ([6370343](https://github.com/pproenca/dot-claude/commit/6370343ce789089eaa9580e5ab748e3955499144))
* fix stale skill names and remove non-existent Cursor section ([2d56d26](https://github.com/pproenca/dot-claude/commit/2d56d2635d2fcf6be1be99ed0d936de6bf2f8a69))
* **init:** update claude to use 'uv' for python ([8f23dba](https://github.com/pproenca/dot-claude/commit/8f23dbabe0e5ad5256033154571f2416d0541ce1))
* mark migration complete in MIGRATION.md ([739c71c](https://github.com/pproenca/dot-claude/commit/739c71c07445e2403d0561b958f6f13e508adeff))
* **python:** add fallback text for graceful degradation (Phase 5) ([2f96c00](https://github.com/pproenca/dot-claude/commit/2f96c000760581028847f0e0da30578fa1aeec1b))
* **python:** update skills and agent to use uv consistently ([8ecc453](https://github.com/pproenca/dot-claude/commit/8ecc45385f901d4fb362ba075817d3a841d52af0))
* remove deprecated plan ([43f0660](https://github.com/pproenca/dot-claude/commit/43f06604557a128bbb343f0b555cca4a8230dfae))
* remove super plugin from CLAUDE.md ([7994ff4](https://github.com/pproenca/dot-claude/commit/7994ff4cb35de7b124502c6289c18c9d5cf913a4))
* **super:** add code-review-standards reference ([cfcc8a7](https://github.com/pproenca/dot-claude/commit/cfcc8a76c388bc19301917d5be9dceb4f4d27c41))
* update CLAUDE.md for new plugin architecture (Phase 6) ([460bef3](https://github.com/pproenca/dot-claude/commit/460bef3f66672608e404936d1c79b96e31f3351f))
* update instructions to use uv consistently ([9dbd01b](https://github.com/pproenca/dot-claude/commit/9dbd01bee4b0b3dd7a66f2fa069bfb4b407cfaeb))
* update README for super plugin removal ([3d2c63a](https://github.com/pproenca/dot-claude/commit/3d2c63aaf3f5cf22420046468d591fa9d7fa8e7e))
* update structure ([b729916](https://github.com/pproenca/dot-claude/commit/b729916d0250307d89ea8f2df9dc16d4eeca00e0))
* update workflow and doc plugins to use uv ([b4d57ae](https://github.com/pproenca/dot-claude/commit/b4d57ae7fbd1b98f4b98a75a341cc4b65eb973b4))


### Maintenance

* reset versioning to 1.0.0 ([404526c](https://github.com/pproenca/dot-claude/commit/404526cf36ccd40db43203c3a64a6ae741cd9eb2))

## Changelog

All notable changes to this project will be documented in this file.
