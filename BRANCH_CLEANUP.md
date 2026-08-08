# Branch cleanup — keep launch branch only

**Keep:** `Python-3` (current launch)

**Protected (do not delete without care):** `develop`

## Delete these old / previous-launch branches

Run from a machine with `gh` auth as Evank253:

```bash
REPO=Evank253/KCN-SUPER-COGNITIVE-HUMAN-GOVERNED-INTELLIGENCE-ECOSYSTEM-

# Old ecosystem name branch
gh api -X DELETE "repos/$REPO/git/refs/heads/KCN-SUPER-COGNITIVE-ECOSYSTEM"

# Copilot / previous launch noise
for b in \
  copilot/add-ci-workflow-automation \
  copilot/align-vercel-deployment-setup \
  copilot/build-verify-docker-images \
  copilot/change-default-branch-to-main \
  copilot/delete-copilot-change-default-branch-to-main \
  copilot/fix-bug-in-core-module \
  copilot/fix-ci-deployment-issues \
  copilot/fix-failing-github-actions-job \
  copilot/fix-failing-github-actions-job-again \
  copilot/fix-frontend-nodejs-20-job \
  copilot/fix-github-actions-frontend-nodejs-20 \
  copilot/fix-github-actions-job-backend-python-3-12 \
  copilot/fix-github-actions-job-frontend \
  copilot/fix-github-actions-job-python-3-12 \
  copilot/fix-github-actions-node-job \
  copilot/fix-that \
  copilot/fix-vercel-deployment-setup \
  copilot/install-vercel-cli-setup-instructions \
  copilot/kcn-phase-2-sprint-1-backend-foundation \
  copilot/kcn-super-cognitive-ecosystem \
  copilot/reference-action-failure \
  copilot/set-up-branch-protection-rules \
  copilot/update-landingpage-portal-interface \
  copilot/verify-fixes-in-pr-16 \
  fix/frontend-backend-ci-and-deploy \
  vercel/install-and-configure-vercel-s-87688w
do
  echo "Deleting $b"
  gh api -X DELETE "repos/$REPO/git/refs/heads/$b" || true
done

# Optional: set default branch to Python-3 in repo Settings → Branches
```

## vibe-developer

**Keep:** `Python-3`

Delete:
```bash
REPO=Evank253/vibe-developer
for b in \
  copilot/analyze-npm-dependencies \
  copilot/audit-fix-evank253-repos \
  copilot/fix-ci-build-failure \
  copilot/fix-dependency-bump-issue \
  copilot/fix-failing-build-and-test-job \
  copilot/fix-vibedev-end-to-end \
  copilot/research-vite-dependency-issue \
  copilot/vibe-dev-fix-app-functionality \
  dependabot/npm_and_yarn/client/npm_and_yarn-62ce72d0a2 \
  dependabot/npm_and_yarn/dotenv-17.4.2 \
  dependabot/npm_and_yarn/express-5.2.1 \
  dependabot/npm_and_yarn/helmet-8.3.0 \
  dependabot/npm_and_yarn/multer-2.2.0 \
  revert-2-dependabot/npm_and_yarn/multi-989e1d6724
do
  gh api -X DELETE "repos/$REPO/git/refs/heads/$b" || true
done
```

## kcn-preflight

**Keep:** `Python-3`  
Optional delete: `main` only if default is switched to Python-3 first.

## After cleanup

Default branch should be **Python-3** for launch repos.
