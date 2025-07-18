#!/bin/bash

set -euo pipefail

# Function to derive GitHub org from repository list
derive_github_org() {
    local repos="$1"
    if [[ -n "$repos" ]]; then
        # Extract org from first repository (format: org/repo)
        echo "$repos" | cut -d',' -f1 | cut -d'/' -f1
    fi
}

# Check if GITHUB_ORG is set, if not try to derive it
if [[ -z "${GITHUB_ORG:-}" ]]; then
    # Try to derive from REPO parameter first, then GITHUB_REPOS env var
    DERIVED_ORG=$(derive_github_org "${3:-${GITHUB_REPOS:-}}")
    if [[ -n "$DERIVED_ORG" ]]; then
        GITHUB_ORG="$DERIVED_ORG"
        echo "Derived GitHub org: $GITHUB_ORG" >&2
    else
        echo "Error: GITHUB_ORG environment variable is not set and cannot be derived from repositories" >&2
        echo "Please set GITHUB_ORG or provide repositories in format 'org/repo'" >&2
        exit 1
    fi
fi

# Function to get target date
get_target_date() {
    local day="$1"

    if [[ -n "$day" ]]; then
        case "$day" in
            monday|mon)
                date -d "last monday" +%Y-%m-%d 2>/dev/null || date -v-monday +%Y-%m-%d ;;
            tuesday|tue)
                date -d "last tuesday" +%Y-%m-%d 2>/dev/null || date -v-tuesday +%Y-%m-%d ;;
            wednesday|wed)
                date -d "last wednesday" +%Y-%m-%d 2>/dev/null || date -v-wednesday +%Y-%m-%d ;;
            thursday|thu)
                date -d "last thursday" +%Y-%m-%d 2>/dev/null || date -v-thursday +%Y-%m-%d ;;
            friday|fri)
                date -d "last friday" +%Y-%m-%d 2>/dev/null || date -v-friday +%Y-%m-%d ;;
            saturday|sat)
                date -d "last saturday" +%Y-%m-%d 2>/dev/null || date -v-saturday +%Y-%m-%d ;;
            sunday|sun)
                date -d "last sunday" +%Y-%m-%d 2>/dev/null || date -v-sunday +%Y-%m-%d ;;
            yesterday)
                date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d ;;
            *)
                date -d "$day" +%Y-%m-%d 2>/dev/null || date -j -f "%Y-%m-%d" "$day" +%Y-%m-%d ;;
        esac
    else
        # Default to last workday
        local dow=$(date +%u)
        case $dow in
            1) local days=3 ;; # Monday -> Friday
            *) local days=1 ;; # Any other day -> yesterday
        esac
        date -d "-$days days" +%Y-%m-%d 2>/dev/null || date -v-${days}d +%Y-%m-%d
    fi
}

# Function to get detailed event information
get_event_details() {
    local event_type="$1"
    local repo="$2"
    local payload="$3"

    echo "Event Type: $event_type"
    echo "Repository: $repo"

    case "$event_type" in
        "PushEvent")
            local push_ref=$(echo "$payload" | jq -r '.ref // "unknown"')
            local push_size=$(echo "$payload" | jq -r '.size // 0')
            local branch_name=$(echo "$push_ref" | sed 's|refs/heads/||')
            echo "  Branch: $push_ref ($push_size commits)"
            echo "  Branch Link: https://github.com/$repo/tree/$branch_name"

            # Extract and deduplicate commits
            local commits_json=$(echo "$payload" | jq -c --arg username "$4" '
                [.commits[]?
                | select(.message != null and .message != "")
                | select(if $username != "" then
                    ((.author.email // "") | ascii_downcase | test($username | ascii_downcase)) or
                    ((.author.name // "") | ascii_downcase | test($username | ascii_downcase)) or
                    ((.committer.email // "") | ascii_downcase | test($username | ascii_downcase)) or
                    ((.committer.name // "") | ascii_downcase | test($username | ascii_downcase))
                  else true end)]
            ' 2>/dev/null)

            if [[ "$commits_json" != "[]" && "$commits_json" != "null" ]]; then
                echo "$commits_json" | jq -r '.[] | .message + "|" + .sha[0:7] + "|" + .sha' 2>/dev/null | while IFS='|' read -r commit_message commit_sha full_sha; do
                    if [[ -n "$commit_message" && -n "$commit_sha" ]]; then
                        # Create a key for deduplication (normalize message and escape special chars)
                        local commit_key=$(echo "$commit_message" | tr -d '\n\r' | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9 ]/_/g')

                        # Check if we've seen this commit message before
                        if ! grep -qF "$commit_key|" "$SEEN_COMMITS_FILE" 2>/dev/null; then
                            echo "$commit_key|$commit_sha" >> "$SEEN_COMMITS_FILE"
                            echo "    • $commit_message ($commit_sha) - https://github.com/$repo/commit/$full_sha"
                        fi
                    fi
                done
            fi

            # If no commits matched author filter, show all commits with deduplication
            local commit_count=$(echo "$payload" | jq -r '.commits | length')
            if [[ "$commits_json" == "[]" && "$commit_count" -gt 0 ]]; then
                echo "    (No commits matched author filter - showing all commits:)"
                echo "$payload" | jq -r '.commits[] | (.message // "empty") + "|" + .sha[0:7] + "|" + (.author.name // "unknown") + "|" + .sha' 2>/dev/null | while IFS='|' read -r commit_message commit_sha commit_author full_sha; do
                    if [[ -n "$commit_message" && "$commit_message" != "empty" ]]; then
                        local commit_key=$(echo "$commit_message" | tr -d '\n\r' | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9 ]/_/g')

                        if ! grep -qF "$commit_key|" "$SEEN_COMMITS_FILE" 2>/dev/null; then
                            echo "$commit_key|$commit_sha" >> "$SEEN_COMMITS_FILE"
                            echo "    • $commit_message ($commit_sha) by $commit_author - https://github.com/$repo/commit/$full_sha"
                        fi
                    fi
                done
            fi
            ;;
        "PullRequestEvent")
            local pr_number=$(echo "$payload" | jq -r '.pull_request.number // empty')
            local pr_action=$(echo "$payload" | jq -r '.action // empty')
            if [[ -n "$pr_number" ]]; then
                echo "  PR #$pr_number: https://github.com/$repo/pull/$pr_number"
                if [[ "$pr_action" == "opened" ]]; then
                    local pr_details=$(gh api "/repos/$repo/pulls/$pr_number" 2>/dev/null || echo '{}')
                    echo "$pr_details" | jq -r '
                        "  Title: " + (.title // "No title") + "\n" +
                        "  Description: " + ((.body // "No description") | .[0:200]) +
                        (if (.body // "" | length) > 200 then "..." else "" end)
                    ' 2>/dev/null
                else
                    echo "  Action: $pr_action"
                fi
            fi
            ;;
        "IssueCommentEvent")
            local issue_number=$(echo "$payload" | jq -r '.issue.number // empty')
            local is_pull_request=$(echo "$payload" | jq -r '.issue.pull_request != null')
            if [[ -n "$issue_number" ]]; then
                if [[ "$is_pull_request" == "true" ]]; then
                    echo "  PR #$issue_number Comment: https://github.com/$repo/pull/$issue_number"
                else
                    echo "  Issue #$issue_number Comment: https://github.com/$repo/issues/$issue_number"
                fi
            fi
            echo "$payload" | jq -r '
                "  Comment: " + ((.comment.body // "No comment") | .[0:150]) +
                (if (.comment.body // "" | length) > 150 then "..." else "" end)
            ' 2>/dev/null
            ;;
        "PullRequestReviewEvent")
            local pr_number=$(echo "$payload" | jq -r '.pull_request.number // empty')
            if [[ -n "$pr_number" ]]; then
                echo "  PR #$pr_number: https://github.com/$repo/pull/$pr_number"
            fi
            echo "$payload" | jq -r '
                "  Review: " + (.review.state // "No state") +
                (if .review.body and .review.body != "" then
                    " - " + (.review.body | .[0:100]) +
                    (if (.review.body | length) > 100 then "..." else "" end)
                else "" end)
            ' 2>/dev/null
            ;;
        "CreateEvent")
            echo "$payload" | jq -r '
                "  Created: " + (.ref_type // "unknown") +
                (if .ref then " \"" + .ref + "\"" else "" end)
            ' 2>/dev/null
            ;;
        "DeleteEvent")
            echo "$payload" | jq -r '
                "  Deleted: " + (.ref_type // "unknown") +
                (if .ref then " \"" + .ref + "\"" else "" end)
            ' 2>/dev/null
            ;;
        "PullRequestReviewCommentEvent")
            local pr_number=$(echo "$payload" | jq -r '.pull_request.number // empty')
            if [[ -n "$pr_number" ]]; then
                echo "  PR #$pr_number Review Comment: https://github.com/$repo/pull/$pr_number"
            fi
            ;;
    esac
}

# Function to get all events from a repo with pagination
get_repo_events() {
    local repo="$1"
    local target_date="$2"
    local username="$3"
    local start_date="$4"
    local end_date="$5"
    local page=1
    local per_page=100

    while true; do
        local events=$(gh api "/repos/$repo/events?page=$page&per_page=$per_page" 2>/dev/null || echo "[]")

        # Check if response is valid JSON and is an array
        if ! echo "$events" | jq -e 'type == "array"' >/dev/null 2>&1; then
            break
        fi

        # Check if we got any events
        local count=$(echo "$events" | jq length 2>/dev/null || echo "0")
        count=$(echo "$count" | tr -d '\n\r ')  # Remove whitespace/newlines
        if [[ "$count" -eq 0 ]] 2>/dev/null || [[ -z "$count" ]]; then
            break
        fi

        # Filter events for target date range and username
        echo "$events" | jq -c --arg start_date "$4" --arg end_date "$5" --arg username "$username" '
            .[]
            | select(.created_at >= $start_date and .created_at <= $end_date)
            | select(if $username == "" then true else
                (.actor.login == $username) or
                (.actor.login | ascii_downcase == ($username | ascii_downcase))
              end)
        ' 2>/dev/null | while IFS= read -r event; do
            if [[ -n "$event" ]]; then
                local created_at=$(echo "$event" | jq -r '.created_at')
                local event_type=$(echo "$event" | jq -r '.type')
                local repo_name=$(echo "$event" | jq -r '.repo.name // "unknown"')
                local actor=$(echo "$event" | jq -r '.actor.login')
                local payload=$(echo "$event" | jq -r '.payload')

                echo "[$created_at] $event_type in $repo_name by $actor"
                get_event_details "$event_type" "$repo" "$payload" "$username"
                echo ""
            fi
        done

        # Check if we've gone past our target date range (events are sorted by date desc)
        local oldest_timestamp=$(echo "$events" | jq -r '.[-1].created_at // empty' 2>/dev/null)
        if [[ -n "$oldest_timestamp" && "$oldest_timestamp" < "$start_date" ]]; then
            break
        fi

        ((page++))

        # Safety check to avoid infinite loops
        if [[ $page -gt 50 ]]; then
            break
        fi
    done
}

# File to track seen commit messages for deduplication
SEEN_COMMITS_FILE="/tmp/github-activity-seen-commits.$$"
> "$SEEN_COMMITS_FILE"  # Initialize empty file

# Main script
DAY="${1:-}"
USERNAME="${2:-}"
REPO="${3:-}"
TARGET_DATE=$(get_target_date "$DAY")

# Convert target date to UTC range to handle timezone issues
# GitHub API returns UTC times, but we want to match local work days
TARGET_DATE_START="${TARGET_DATE}T00:00:00Z"
# Include the next day until 11:59 PM to catch late night work in UTC
NEXT_DATE=$(date -d "$TARGET_DATE + 1 day" +%Y-%m-%d 2>/dev/null || date -v+1d -j -f "%Y-%m-%d" "$TARGET_DATE" +%Y-%m-%d)
TARGET_DATE_END="${NEXT_DATE}T07:59:59Z"  # Covers up to midnight-8am next day UTC (covers most US timezones)

# Use provided REPO param, or fallback to GITHUB_REPOS environment variable
REPOS_TO_CHECK="${REPO:-${GITHUB_REPOS:-}}"

if [[ -n "$REPOS_TO_CHECK" ]]; then
    # Specific repo(s) mode
    IFS=',' read -ra REPO_LIST <<< "$REPOS_TO_CHECK"
    if [[ -n "$USERNAME" ]]; then
        echo "Getting GitHub activity for user '$USERNAME' in ${#REPO_LIST[@]} repo(s) on $TARGET_DATE..."
    else
        echo "Getting GitHub activity for ${#REPO_LIST[@]} repo(s) on $TARGET_DATE..."
    fi

    for repo in "${REPO_LIST[@]}"; do
        repo=$(echo "$repo" | xargs)  # trim whitespace
        if [[ -n "$repo" ]]; then
            get_repo_events "$repo" "$TARGET_DATE" "$USERNAME" "$TARGET_DATE_START" "$TARGET_DATE_END"
        fi
    done
else
    # All repos mode
    if [[ -n "$USERNAME" ]]; then
        echo "Getting GitHub activity for user '$USERNAME' in $GITHUB_ORG on $TARGET_DATE..."
    else
        echo "Getting GitHub activity for $GITHUB_ORG on $TARGET_DATE..."
    fi

    # Get all repos in the org with pagination
    gh api "/orgs/$GITHUB_ORG/repos" --paginate | jq -r '.[].full_name' | while read -r repo; do
        if [[ -n "$repo" ]]; then
            get_repo_events "$repo" "$TARGET_DATE" "$USERNAME" "$TARGET_DATE_START" "$TARGET_DATE_END"
        fi
    done
fi

# Cleanup
rm -f "$SEEN_COMMITS_FILE" 2>/dev/null
