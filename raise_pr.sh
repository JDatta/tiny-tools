#!/bin/bash

#
# Given a set of commit ids and some branch names in upstream remote, this
# script creates separate brances off different upstream branch and
# cherry-picks the commits. It then pushes the branches and also opens the
# pull request creation pages in github.com
#
# This assumes
#  1. No merge conflicts
#  2. No password prompts while accessing remote git repositories.

# Configurables
PROJECT_DIR="/path/to/your/git/repository"
BRANCH_PREFIX="feature-name"
BRANCHES="version1 version2 develop"
COMMITS="commit_id1 commit_id2"
REMOTE_NAME="upstream"
GITHUB_REPO_URL="https://github.com/Company/repository"

cd $PROJECT_DIR

git fetch ${REMOTE_NAME}

for branch in $BRANCHES; do
  echo "Creating pull request for $branch"
  git checkout -b "${BRANCH_PREFIX}/${branch}" "${REMOTE_NAME}/${branch}"
  git cherry-pick ${COMMITS}
  git push origin "${BRANCH_PREFIX}/${branch}"
  xdg-open ${GITHUB_REPO_URL}/compare/${branch}...JDatta:"${BRANCH_PREFIX}/${branch}"
done

