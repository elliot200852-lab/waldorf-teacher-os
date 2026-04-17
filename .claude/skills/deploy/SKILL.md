---
aliases:
  - "部署技能"
---

# Deploy Workflow
1. Run `firebase deploy --only hosting`
2. Confirm deployment URL is live
3. Run `git add -A && git commit -m "$COMMIT_MESSAGE"` (ask user for message if not provided)
4. Run `git push origin $(git branch --show-current)`
5. Confirm push succeeded
Never skip the git push step.
