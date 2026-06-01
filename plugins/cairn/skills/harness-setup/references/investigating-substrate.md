# How to investigate an unfamiliar repo's substrate

This is a METHOD, not a list. There is deliberately no table of "go.mod means Go,
Cargo.toml means Rust" here, because a table is someone else's answer frozen in
time — you would inherit it without understanding it, could not maintain it when a
convention shifts, and could not extend it to an ecosystem no one listed. A method
you run yourself produces facts you OWN: you know why each is true because you
derived it, and it works on a language invented tomorrow because the method does
not care which language — it cares how to find out.

A human meeting an unfamiliar repo does not recite a lookup. They look around: what
is the manifest, what does it say, how is the code actually laid out, does my guess
match what I see. That looking is this method. You already have the faculties to run
it — this just composes them.

## The method (this is `inquiry`, pointed at the repo's substrate)

1. **Predict, before looking.** State what you think the substrate is and a
   confidence. On no evidence, that confidence is low — say so. Do not assume the
   stack you have seen most; that is the bias that writes a config for a project
   that does not exist.

2. **Find the cheapest discriminating observation: the manifest.** Nearly every
   ecosystem declares itself in a root manifest/build file. Look for one. Its NAME
   and CONTENTS identify the substrate more reliably than source extensions (which
   can be ambiguous or absent). One file read usually settles it. If several
   manifests coexist, that is itself a finding: a polyglot repo or a monorepo, to
   be investigated per workspace, not flattened into one guess.

3. **Derive the conventions from what the manifest implies and the tree confirms.**
   Once you know the ecosystem, you know where to look for its conventions — but
   CONFIRM them against the actual directories rather than assuming. Where does this
   repo keep its domain types, its boundaries/ports, its entry points, its tests?
   Read the tree; let it correct your expectation. The layer mapping is a prediction
   you falsify against the real layout.

4. **Derive the verify commands the same way.** How does THIS repo build and test?
   The manifest and its scripts/targets usually say. Confirm; do not hardcode a
   command from memory of another stack.

5. **Record what you derived as a fact you now own.** Write the finding to
   `library-knowledge` — substrate name, its marker, where each layer conventionally
   lives, how it builds — keyed by the substrate name. Next time you meet this
   substrate you recall YOUR finding, not a stranger's table; and because you
   derived it, you can update it when you learn better. The table builds itself,
   one owned entry at a time, from your real encounters.

6. **When the investigation itself repeats, build a tool for it.** The third time
   you hand-investigate the same ecosystem, that is `toolsmith`'s trigger: forge a
   detector for it. The detector is yours, built because you understood the method —
   not a constant handed to you.

## The honesty that keeps this unbiased
You are deriving, not looking up. So: report confidence, and when you cannot
identify the substrate, REFUSE to default — record "unknown, investigated, here is
what I observed" rather than asserting a familiar stack. A wrong default propagates
silently into every later solve. "I do not yet know this substrate; here is what I
found and what I could not determine" is the honest, ownable output.

## Why there is no list in this file
If a future version of this document grows a table of substrates and their
conventions, distrust it — it means someone has started doing your investigating
for you again, and you have started inheriting facts you do not own. The facts
belong in YOUR library-knowledge store, derived and maintained by you. This file
holds only the method.
