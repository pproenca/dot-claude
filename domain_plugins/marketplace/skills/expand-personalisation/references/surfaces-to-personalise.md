# Surfaces to Personalise

A master menu of surfaces a two-sided marketplace can personalise beyond the obvious listing feed. Use this as the prompting menu when running `/marketplace:expand-personalisation audit`, and as a reference for engineers brainstorming new surfaces.

Organized by **position in the user journey**. Every surface includes:
- **What it is** — a one-line definition
- **Stage** — where in the journey it lives
- **Typical leverage** — low / medium / high / very high
- **Typical feasibility blockers** — what usually gates the work
- **Key rule references** from the knowledge libraries

> The point of this list is **completeness, not prescription**. Each surface is a candidate; the right ones for any company depend on their surfaces.md, events.md, and north-star.

---

## Anonymous stage (no user identity)

### 1. Landing page hero

**What**: The above-the-fold content on the main landing page for anonymous visitors.
**Leverage**: very high (it's the first render for organic + paid traffic)
**Feasibility**: medium — requires signal inference (role, geo, inbound channel) before first byte
**Blockers**: often constrained by SEO / cache / CDN strategy, so personalised rendering needs edge logic
**Rules**: `signal-extract-role-from-url-and-referrer`, `signal-infer-geography-with-confidence`, `signal-classify-inbound-intent`

### 2. Landing page trust block

**What**: Safety / guarantee / social proof copy on the landing page.
**Leverage**: high (big conversion lever for high-anxiety categories)
**Feasibility**: high — variants can be rendered client-side after first paint
**Blockers**: requires honest local proof, not aggregate platitudes
**Rules**: `owner-show-specific-local-reviews`, `owner-surface-safety-guarantees-prominently`, `proof-localise-social-proof-to-visitor-area`

### 3. Anonymous search autocomplete

**What**: Suggestions as the visitor types in the search box before signing up.
**Leverage**: medium
**Feasibility**: high — no identity required, personalisation by session signal (geo, inbound query)
**Blockers**: zero if autocomplete exists; full rebuild if it doesn't
**Rules**: `query-build-autocomplete-on-separate-index`, `signal-classify-inbound-intent`

### 4. Anonymous search result ordering

**What**: Results for the visitor's first searches before they register.
**Leverage**: high (search is high-intent traffic)
**Feasibility**: medium — depends on available anonymous signals
**Blockers**: most ranking models assume authenticated users; fallback to popularity-by-segment
**Rules**: `arch-design-for-cold-start-from-day-one`, `cold-best-of-segment-popularity`, `signal-classify-inbound-intent`

### 5. Zero-result fallback (anonymous)

**What**: What the visitor sees when a query returns no results.
**Leverage**: medium (catches high-intent visitors who'd otherwise bounce)
**Feasibility**: high
**Blockers**: none
**Rules**: `blend-never-return-zero-results`, `arch-design-zero-result-fallback`

### 6. Landing page "featured" strip

**What**: Curated or algorithmic list of featured listings / destinations / themes on the landing page.
**Leverage**: medium
**Feasibility**: high
**Blockers**: needs a cold-start solution for anonymous visitors
**Rules**: `cold-best-of-segment-popularity`, `cold-reserve-exploration-slots`

### 7. Seasonal / themed collections

**What**: "Winter sun", "pet-friendly long stays", "city breaks" feature units.
**Leverage**: medium
**Feasibility**: high
**Blockers**: requires content curation capacity
**Rules**: `arch-route-surfaces-deliberately`, `cold-reserve-exploration-slots`

---

## Registered pre-paid stage (identified, not yet paid)

### 8. Onboarding intent capture branches

**What**: The order and content of onboarding questions based on role + inferred signal.
**Leverage**: very high (sets the anchor for everything downstream)
**Feasibility**: high (rule-based works well; signal already captured)
**Blockers**: requires a mutable onboarding engine that can branch mid-flow
**Rules**: `onboard-ask-role-before-anything-else`, `onboard-ask-highest-information-gain-first`, `onboard-prefill-from-inferred-signal`, `onboard-allow-answer-revision-without-restart`

### 9. Onboarding pacing

**What**: How fast and how much to ask at once; which questions to defer until later.
**Leverage**: high
**Feasibility**: high
**Blockers**: requires tracking partial-profile state and deferred prompts
**Rules**: `onboard-make-optional-questions-genuinely-skippable`, `profile-build-incrementally-on-each-interaction`

### 10. Paywall screen copy and layout

**What**: The messaging and layout of the paywall for registered-but-not-paid users.
**Leverage**: very high (single highest-conversion-weight impression in the funnel)
**Feasibility**: medium — needs cohort inference and variant rendering
**Blockers**: often owned by a different team from recsys
**Rules**: `convert-anchor-price-against-local-alternative`, `convert-use-loss-aversion-framing-on-soft-locks`, `owner-anchor-cost-against-local-alternative`

### 11. Paywall timing / trigger

**What**: When to show the paywall — on specific-listing click, after N sessions, after a dwell threshold.
**Leverage**: very high
**Feasibility**: high
**Blockers**: requires event-stream triggering
**Rules**: `convert-trigger-paywall-on-specific-listings`, `convert-never-interrupt-active-search`

### 12. Soft-lock experiences

**What**: Content the user "builds" (saved searches, favorites, profile) that gets soft-locked until payment.
**Leverage**: high
**Feasibility**: high
**Blockers**: requires server-side persistence of anonymous state
**Rules**: `convert-use-loss-aversion-framing-on-soft-locks`, `stitch-preserve-profile-across-registration`

### 13. Paywall alternatives routing

**What**: Suggesting alternative tiers or partial unlocks when the visitor is an unworkable fit for full paid.
**Leverage**: medium (catches high-intent visitors who'd otherwise bounce)
**Feasibility**: medium
**Blockers**: requires eligibility inference
**Rules**: `gap-route-unworkable-segments-to-alternatives`

### 14. Re-engagement email (non-converting registrants)

**What**: Follow-up emails to users who registered but haven't paid.
**Leverage**: medium-high
**Feasibility**: high (email systems are usually mature)
**Blockers**: none
**Rules**: `convert-re-engage-non-converting-registrants-personalised`, `proof-use-specific-peer-stories-not-aggregates`

### 15. Abandoned-browse email

**What**: Email triggered when a visitor browses listings but leaves without converting.
**Leverage**: medium-high
**Feasibility**: medium — blocked on identity stitching for anonymous browsers
**Blockers**: needs cross-device identity, attribution, and consent
**Rules**: `stitch-use-deterministic-matching-for-returning-visitors`, `measure-attribute-conversion-to-signal-change`

---

## Paid pre-active stage (paid, not yet booked)

### 16. First-stay path (new supplier)

**What**: A concrete step-by-step path to the new supplier's first acceptance.
**Leverage**: very high (cold-start cliff for new suppliers)
**Feasibility**: medium — needs per-supplier state machine
**Blockers**: none major
**Rules**: `sitter-provide-concrete-first-stay-path`, `sitter-be-honest-about-first-stay-competition`, `gap-warn-about-cold-start-penalty`

### 17. Profile-completion nudges

**What**: Progressive nudges for paid users to complete their profile (photos, bio, verification).
**Leverage**: high (completeness strongly correlates with first-stay success)
**Feasibility**: high
**Blockers**: none
**Rules**: `profile-build-incrementally-on-each-interaction`, `stitch-preserve-profile-across-registration`

### 18. First-week discovery feed

**What**: A different homefeed experience for users in their first week of paid use.
**Leverage**: high
**Feasibility**: medium — requires user age as a feature and a distinct fallback
**Blockers**: cold-start strategy must differ from the default fallback
**Rules**: `cold-best-of-segment-popularity`, `cold-tag-cold-start-recs`, `cold-use-v2-recipe-with-metadata`

### 19. "What to do next" module

**What**: An explicit list of next actions (complete profile, save 3 listings, message your first supplier).
**Leverage**: high
**Feasibility**: high
**Blockers**: none
**Rules**: `sitter-provide-concrete-first-stay-path`, `profile-build-incrementally-on-each-interaction`

---

## Active stage (using the product)

### 20. Homefeed (main discovery surface)

**What**: The default landing surface after login.
**Leverage**: very high
**Feasibility**: depends on events and identity state (usually the most mature surface)
**Blockers**: feedback-loop bias risk is very high
**Rules**: `arch-split-candidate-generation-from-ranking`, `recipe-default-to-user-personalization-v2`, `loop-detect-death-spirals`, `match-cap-provider-exposure`

### 21. Search result ranking

**What**: The order of results in the search page.
**Leverage**: very high (high-intent traffic)
**Feasibility**: depends on existing retrieval infrastructure
**Blockers**: golden-set must exist before shipping ranker changes
**Rules**: `rank-deploy-ltr-only-after-golden-set-exists`, `rank-normalise-scores-across-retrieval-primitives`, `rank-use-function-score-for-business-signals`

### 22. Search autocomplete (post-login)

**What**: Suggestions as the user types, personalised to their profile and past searches.
**Leverage**: medium-high
**Feasibility**: high
**Blockers**: needs a separate index (not the main one) for speed
**Rules**: `query-build-autocomplete-on-separate-index`

### 23. Zero-result fallback (post-login)

**What**: What the user sees when their search returns nothing.
**Leverage**: medium (filters queries from bouncing)
**Feasibility**: high
**Blockers**: none
**Rules**: `blend-never-return-zero-results`, `arch-design-zero-result-fallback`

### 24. Related / similar listings on detail page

**What**: "Similar to this one" / "people who viewed this also viewed" on the listing detail page.
**Leverage**: medium-high
**Feasibility**: high (item-to-item is a well-understood problem)
**Blockers**: needs to respect pet / date / location filters
**Rules**: `recipe-sims-for-item-page-only`, `rank-use-function-score-for-business-signals`

### 25. Review ordering on listing pages

**What**: Which reviews to surface first on a listing detail page.
**Leverage**: medium
**Feasibility**: high
**Blockers**: none
**Rules**: `proof-source-stories-from-real-history-not-handpicked`, `proof-surface-mixed-reviews-not-only-five-star`

### 26. Saved search alerts

**What**: Email / push triggered when a new listing matches a saved search.
**Leverage**: high (high-intent and high-engagement)
**Feasibility**: high
**Blockers**: requires a frequency / staleness policy to avoid spam
**Rules**: `convert-never-interrupt-active-search`, `profile-decay-features-with-inactivity`

### 27. Messaging template suggestions

**What**: Suggested first-message templates when contacting a new counterparty.
**Leverage**: medium (improves first-message quality → acceptance rate)
**Feasibility**: medium
**Blockers**: requires moderation / quality gating
**Rules**: `sitter-provide-concrete-first-stay-path`

### 28. Map / geography defaults on search

**What**: Default map focus when the user opens search.
**Leverage**: medium
**Feasibility**: high
**Blockers**: none
**Rules**: `signal-infer-geography-with-confidence`

### 29. Search filter defaults

**What**: Default date range, pet type, amenities when search opens.
**Leverage**: medium
**Feasibility**: high
**Blockers**: requires profile state
**Rules**: `profile-build-incrementally-on-each-interaction`

### 30. Category / theme collections (post-login)

**What**: Curated themes appropriate for the user's inferred profile.
**Leverage**: medium
**Feasibility**: high
**Blockers**: none
**Rules**: `arch-route-surfaces-deliberately`

### 31. Push notification timing

**What**: When to send push notifications to maximize engagement without fatigue.
**Leverage**: medium
**Feasibility**: high
**Blockers**: requires quiet-hours, frequency cap logic
**Rules**: `profile-decay-features-with-inactivity`

### 32. Push notification content

**What**: Which piece of content to push (new match, saved search alert, message reply, price drop).
**Leverage**: medium
**Feasibility**: high
**Blockers**: needs a per-user interest inference
**Rules**: `proof-use-specific-peer-stories-not-aggregates`

---

## Retained / retention stage

### 33. Renewal reminder timing and copy

**What**: When and how to prompt the user to renew their membership.
**Leverage**: very high (direct revenue)
**Feasibility**: high
**Blockers**: requires engagement-based segmentation
**Rules**: `convert-use-loss-aversion-framing-on-soft-locks`, `proof-use-specific-peer-stories-not-aggregates`

### 34. Tier-upgrade prompts

**What**: When to show "upgrade to premium" prompts.
**Leverage**: medium-high (Premium retention lever)
**Feasibility**: high
**Blockers**: needs frequency-based segmentation (who actually benefits from Premium)
**Rules**: `convert-anchor-price-against-local-alternative`, `convert-never-interrupt-active-search`

### 35. Referral prompt timing

**What**: When to ask an engaged user to refer a friend.
**Leverage**: medium
**Feasibility**: high
**Blockers**: none
**Rules**: `proof-use-specific-peer-stories-not-aggregates`

### 36. Lapsed-user re-engagement

**What**: Content and timing of emails / push for users who've been inactive for N days.
**Leverage**: medium
**Feasibility**: medium — requires lifecycle segmentation
**Blockers**: needs a reactivation offer strategy
**Rules**: `profile-decay-features-with-inactivity`, `convert-re-engage-non-converting-registrants-personalised`

### 37. Seasonal campaigns

**What**: Time-of-year campaigns (summer travel, winter escape, year-end planning) personalised by the user's history.
**Leverage**: medium
**Feasibility**: medium — depends on campaign tooling
**Blockers**: often content-creation bound, not tech bound
**Rules**: `arch-route-surfaces-deliberately`

---

## Cross-cutting (any stage)

### 38. Help / support content recommendations

**What**: Which help articles to surface based on the user's likely problem.
**Leverage**: low-medium (indirect; reduces support load)
**Feasibility**: high
**Blockers**: none
**Rules**: `proof-use-specific-peer-stories-not-aggregates`

### 39. Notification preferences defaults

**What**: Pre-fill notification preferences at signup based on inferred role / intent.
**Leverage**: medium (retention lever via correct defaults)
**Feasibility**: high
**Blockers**: requires role inference from onboarding
**Rules**: `onboard-prefill-from-inferred-signal`

### 40. Sidebar / related content on any page

**What**: Contextual related content in a sidebar — "you might also want to look at".
**Leverage**: low-medium
**Feasibility**: high
**Blockers**: none
**Rules**: `arch-route-surfaces-deliberately`

---

## How to use this list

When running `audit` mode:

1. For each entry above, check whether it exists in `surfaces.md`
2. If not listed in `surfaces.md`, ask the user whether the surface exists in the product
3. For surfaces that exist but aren't personalised, score them per the workflow in [SKILL.md](../SKILL.md)
4. For surfaces that don't exist, flag as **product gap** — a new-feature opportunity separate from the personalisation backlog

When running a **named-surface** query, match the user's input fuzzily against this list — "abandoned cart" maps to #15, "new-member feed" maps to #18, etc.

## Living document

This list is complete as of its authoring date but is not exhaustive. Every bootstrap-context session is an opportunity to discover surfaces not on this list — if a user has a surface we haven't catalogued, add it via a skill update.
