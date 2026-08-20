# Slicing

## The test each item must pass

**Independent.** Buildable while every other item does not yet exist. If item B
cannot start until item A ships, either merge them or make A's behaviour a port
with dummy state.

**Negotiable.** States an outcome, not an implementation. "Persist review snapshots"
survives a change of storage engine; "add a Delta table with these six columns"
does not.

**Valuable.** Someone can tell the difference once it lands. An item whose only
effect is that another item becomes easier is refactoring, not a story.

**Estimable.** The analyst can write a plan without new research. If the item needs
a spike to be understood, the spike is the item.

**Small.** One coherent change. If the plan would need more than a handful of
files, or the Gherkin would need more than a few scenarios, slice again.

**Testable.** The project's own test command can prove it. An item that can only be
verified by a human looking at a dashboard needs its observable narrowed until a
test can see it.

## Vertical, not horizontal

Slice through the layers, not along them. "Read the config, validate it, and log
the result for one flag" is a story. "Add the config layer" is not — it delivers
nothing observable and forces every later item to depend on it.

The exception is a genuine seam: when a contract is shared by several items and
getting it wrong is expensive, one item may own the contract and its first real
consumer together.

## Where stories come from in a design document

In order of yield:

1. **Migration or rollout plans** — already ordered, already scoped, usually already
   sliced by someone who understood the dependencies.
2. **Acceptance criteria** — each criterion is at minimum a scenario, often a story.
3. **Keep / reshape / retire / defer inventories** — every reshape and retire is a
   candidate; every defer is an explicit non-goal worth recording.
4. **Contracts and data models** — a story per contract, paired with its first
   consumer.

Narrative sections — decisions, evidence, rejected alternatives, end-state prose —
justify the work. They are not stories, and slicing them produces items with no
observable.

## Failure modes

**The document-as-story.** One item holding an entire design. The analyst produces
one unbuildable plan and the gate rejects it. Slice first.

**The invisible dependency.** Item C quietly assumes item A landed. Caught by
forcing every item to write its `Not in scope` and `Ports` sections.

**The layer story.** "Set up the schema", "add the client", "wire the config".
Nothing observable; the pipeline has nothing to verify and QA has nothing to run.

**The research item.** Written as work when it is really a question. If nobody can
say what finished looks like, the item is a question for the operator, not a story.

**Too many at once.** Twenty items written from one document, nineteen of which are
speculative. Write the ones that are real now; the rest are cheaper to write later,
once the first few have moved.
