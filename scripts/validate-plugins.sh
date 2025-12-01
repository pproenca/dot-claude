#!/usr/bin/env bash
#
# Validates Claude Code plugins in the repository.
#
# Performs four validation checks:
#   1. Repository root validation via claude CLI
#   2. marketplace.json references existing directories
#   3. All plugin directories are listed in marketplace.json
#   4. Individual plugin validation via claude CLI
#
# Returns 0 if all checks pass, 1 if any fail.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_DIR
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
readonly REPO_ROOT
readonly PLUGINS_DIR="${REPO_ROOT}/plugins"
readonly MARKETPLACE_JSON="${REPO_ROOT}/.claude-plugin/marketplace.json"
readonly RELEASE_CONFIG_JSON="${REPO_ROOT}/release-please-config.json"

#######################################
# Outputs error message to stderr.
# Arguments:
#   Error message
#######################################
err() {
  echo "ERROR: $*" >&2
}

#######################################
# Validates marketplace using claude CLI.
# Globals:
#   REPO_ROOT
# Returns:
#   0 if validation passes, 1 otherwise
#######################################
validate_marketplace() {
  echo "Validating marketplace..."
  if ! claude plugin validate "${REPO_ROOT}"; then
    return 1
  fi
}

#######################################
# Validates marketplace.json plugin references exist.
# Globals:
#   REPO_ROOT, MARKETPLACE_JSON
# Returns:
#   0 if all references valid, 1 otherwise
#######################################
validate_marketplace_references() {
  echo ""
  echo "Validating marketplace.json plugin references..."

  local has_error=0
  local plugin_source
  local plugin_path

  while IFS= read -r plugin_source; do
    plugin_path="${REPO_ROOT}/${plugin_source#./}"
    if [[ ! -d "${plugin_path}" ]]; then
      err "marketplace.json references non-existent plugin: ${plugin_source}"
      has_error=1
    fi
  done < <(jq -r '.plugins[].source' "${MARKETPLACE_JSON}")

  return "${has_error}"
}

#######################################
# Validates all plugin directories are listed in marketplace.json.
# Globals:
#   REPO_ROOT, PLUGINS_DIR, MARKETPLACE_JSON
# Returns:
#   0 if all plugins listed, 1 otherwise
#######################################
validate_all_plugins_listed() {
  local has_error=0
  local marketplace_plugins
  local plugin_dir
  local plugin_name
  local relative_path

  marketplace_plugins=$(jq -r '.plugins[].source | sub("^\\./"; "")' "${MARKETPLACE_JSON}")

  for plugin_dir in "${PLUGINS_DIR}"/*/; do
    plugin_name=$(basename "${plugin_dir}")
    relative_path="plugins/${plugin_name}"
    if ! echo "${marketplace_plugins}" | grep -q "^${relative_path}$"; then
      err "Plugin directory not listed in marketplace.json: ${relative_path}"
      has_error=1
    fi
  done

  return "${has_error}"
}

#######################################
# Validates release-please-config.json consistency.
# Globals:
#   REPO_ROOT, MARKETPLACE_JSON, RELEASE_CONFIG_JSON
# Returns:
#   0 if consistency check passes, 1 otherwise
#######################################
validate_release_config_consistency() {
  echo ""
  echo "Validating release-please-config.json consistency..."

  local has_error=0
  local marketplace_plugins
  local plugin_source
  local plugin_json_path

  marketplace_plugins=$(jq -r '.plugins[].source | sub("^\\./"; "")' "${MARKETPLACE_JSON}")

  # Check each plugin is in release-please-config.json
  for plugin_source in ${marketplace_plugins}; do
    plugin_json_path="${plugin_source}/.claude-plugin/plugin.json"
    if ! grep -q "\"path\": \"${plugin_json_path}\"" "${RELEASE_CONFIG_JSON}"; then
      err "Plugin missing from release-please-config.json: ${plugin_source}"
      has_error=1
    fi
  done

  return "${has_error}"
}

#######################################
# Validates each plugin using claude CLI.
# Globals:
#   PLUGINS_DIR
# Returns:
#   0 if all plugins valid, 1 otherwise
#######################################
validate_individual_plugins() {
  echo ""
  echo "Validating plugins..."

  local has_error=0
  local plugin_dir

  for plugin_dir in "${PLUGINS_DIR}"/*/; do
    if ! claude plugin validate "${plugin_dir}"; then
      has_error=1
    fi
  done

  return "${has_error}"
}

#######################################
# Main validation orchestration.
# Returns:
#   0 if all validations pass, 1 otherwise
#######################################
main() {
  local failed=0

  validate_marketplace || failed=1
  validate_marketplace_references || failed=1
  validate_all_plugins_listed || failed=1
  validate_release_config_consistency || failed=1
  validate_individual_plugins || failed=1

  echo ""
  if [[ "${failed}" -eq 0 ]]; then
    echo "All validations passed"
  else
    echo "Some validations failed"
    return 1
  fi
}

main "$@"
