# Google Shell Style Guide - Quick Reference

## Formatting
- [ ] 2-space indentation (no tabs)
- [ ] 80-char max line length
- [ ] `; then` and `; do` on same line as `if`/`for`/`while`
- [ ] Pipelines: one line if fits, else split with `\` and pipe on new line

## Quoting & Variables
- [ ] Use `"${var}"` (braces + quotes)
- [ ] Use `"$@"` for argument passing
- [ ] Quote command substitutions: `"$(command)"`
- [ ] Arrays for lists: `"${array[@]}"`

## Commands
- [ ] Use `$(command)` not backticks
- [ ] Use `[[ ]]` not `[ ]` or `test`
- [ ] Use `(( ))` for arithmetic, not `let`/`expr`/$[]
- [ ] Use `-z`/`-n` for string tests
- [ ] Use `==` not `=` in `[[ ]]`

## Functions
- [ ] `lower_case()` naming (underscores)
- [ ] `local` for all function variables
- [ ] Braces on same line: `func() {`
- [ ] Separate `local` declaration from command substitution

## Naming
- [ ] Variables: `lower_case`
- [ ] Functions: `lower_case` or `package::func`
- [ ] Constants: `UPPER_CASE` with `readonly`

## Structure
- [ ] Functions at top (after constants)
- [ ] `main` function for scripts with multiple functions
- [ ] `main "$@"` as last line
- [ ] No executable code between functions

## Avoid
- [ ] No `eval`
- [ ] No aliases in scripts (use functions)
- [ ] No tabs (except heredoc `<<-`)
- [ ] No pipes to while (use process substitution)
- [ ] No unquoted wildcards (use `./*`)

## Case Statements
- [ ] 2-space indent for alternatives
- [ ] Simple: `pattern) action ;;` on one line
- [ ] Complex: pattern, actions, `;;` on separate lines

## Error Handling
- [ ] Check return values with `if !` or `$?`
- [ ] Use `PIPESTATUS` for pipeline errors
- [ ] Send errors to stderr: `echo "error" >&2`
