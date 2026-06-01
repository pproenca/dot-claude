# Distilling a specialist's soul

The reusable procedure. The output is a *small* profile — the load-bearing few,
not an encyclopedia. If it reads like documentation, it is too long; compress
until only the judgment that changes decisions remains.

## 1. Scope the specialist
Name the domain precisely and say what *mastery* means here. "iOS design" is too
broad; `ios-native-design` scoped to "screens that feel native on iOS 18+ using
the platform's own conventions" is a profile. One domain per profile.

## 2. Confirm current authority (don't trust priors)
Web-confirm best practice from authoritative sources, not the model's memory:
- iOS design → Apple Human Interface Guidelines, current.
- High-performance RN → the React Native performance docs + New Architecture
  guidance for the **confirmed version** (query library-knowledge: RN 0.85).
- Expo → current Expo SDK docs for the confirmed SDK (Expo 56).
Record the sources in `authorities`. This is the same confirm-don't-guess
discipline library-knowledge applies to facts.

## 3. Pin to the facts
Bind the profile to the library-knowledge entries it depends on (`pinned_libs`,
with versions). Craft advice divorced from the real API surface is a stale-config
bug waiting to happen — "use InteractionManager" means nothing if it is about a
version you are not on. The pin is what lets `--check` detect drift.

## 4. Adjudicate contested taste with the user (the human-in-the-loop)
Authority gives the consensus craft; it cannot give *your* app's taste. Surface
the contested, subjective calls to the user the way the spec parse-point surfaces
proposed invariants — and only the contested ones, not the settled consensus.
Examples: large-title vs inline nav, motion intensity, haptics, density,
how far to push platform-native vs brand. Record the answers as `taste_deltas`.
A profile with no taste deltas is fine; a profile that *invented* taste the user
never confirmed is the failure.

## 5. Compress to the load-bearing few
Distill to three sections, each short:
- `principles` — the handful of rules that, if followed, get 80% of the way to
  mastery. (e.g. "respect safe-area + Dynamic Type; never hard-code 44pt — read
  the metrics"; "drive lists with the New-Arch FlatList/FlashList, never .map in
  a ScrollView for unbounded data".)
- `anti_patterns` — what a master *avoids*. Often more diagnostic than the do's
  (e.g. "animating layout on the JS thread"; "blocking the bridge with sync
  bridging calls"; "fixed pixel sizes that ignore Dynamic Type").
- `checklist` — the review questions to run at STAGE 0.5 / build (e.g. "does
  every touch target meet the platform minimum read from metrics?", "is any
  animation driven off the UI thread / native driver?").

## 6. Cache + stamp
Record the profile with `confirmed_on` and `pinned_libs`. From now on it is
applied cheaply and inherited by every feature in the domain; you do not
re-summon the specialist.

## 7. Refresh on drift, not on schedule
Re-distill only when `--check` flags a pinned-lib version mismatch, or the user
says the taste has changed. Refresh is a diff from the recorded profile, not a
relearn. Recurring corrections feed the knowledge-ratchet, which may promote a
principle into a lint rule, a convention, or — on the VENDOR cost test — its own
skill.
