#!/usr/bin/env bash
#
# Full RAG walkthrough: indexes code-base-example (wired in docker-compose.rag.yml),
# then exercises ingest, ask, retrieve, learn, vague, remember, and journal.
# Run from repo root: make -f betteragents.mk test (or bash rag/test.sh).
#
set -euo pipefail

# Run from repo root so betteragents.mk targets work
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

echo "== 1. Starting Docker infrastructure (make -f betteragents.mk up) =="
make -f betteragents.mk up

echo
echo "== 2. Ingesting code-base-example (make -f betteragents.mk ingest) =="
make -f betteragents.mk ingest

echo
echo "== 3. Ask about codebase — prove codebase search (make -f betteragents.mk ask) =="
make -f betteragents.mk ask q="How does the counter work?"

echo
echo "== 4. Retrieve about codebase (make -f betteragents.mk retrieve) =="
make -f betteragents.mk retrieve q="counter flow"

echo
echo "== 5. Teaching memory (make -f betteragents.mk learn, multiple entries) =="
make -f betteragents.mk learn t="Auth: JWT tokens are stored in httpOnly cookies with 15min expiry; refresh tokens use rotating strategy."
make -f betteragents.mk learn t="Payments: Stripe integration handles subscriptions and one-off charges via webhooks."
make -f betteragents.mk learn t="UI: The dashboard shows recent activity and key metrics for the current user."

echo
echo "== 6. Vague pre-flight with hits (make -f betteragents.mk vague) — expect topic summaries =="
make -f betteragents.mk vague q="authentication tokens"

echo
echo "== 7. Vague with no relevant memory (make -f betteragents.mk vague) — expect results=0 =="
make -f betteragents.mk vague q="quantum physics"

echo
echo "== 8. Remember learned knowledge (make -f betteragents.mk remember, classic then verbose) =="
make -f betteragents.mk remember q="What does the agent know about the counter?" m=classic
echo
make -f betteragents.mk remember q="What does the agent know about the counter?" m=verbose

echo
echo "== 9. Retrieve raw chunks (make -f betteragents.mk retrieve) =="
make -f betteragents.mk retrieve q="counter flow"

echo
echo "== 10. Journal work history (make -f betteragents.mk journal, multiple entries) =="
make -f betteragents.mk journal t="Completed counter component refactor: extracted useCounter hook, added increment/decrement/reset actions."
make -f betteragents.mk journal t="Added Stripe webhook handler for subscription.created and subscription.deleted events. TODO: handle payment_failed."
make -f betteragents.mk journal t="Migrated auth flow from cookie-based sessions to JWT httpOnly cookies with 15min expiry. Commits: a1b2c3d."

echo
echo "== 11. Ask about codebase with journal context (make -f betteragents.mk ask) =="
make -f betteragents.mk ask q="What work has been done on the counter?"

echo
echo "== 12. Remember with journal context (make -f betteragents.mk remember verbose) =="
make -f betteragents.mk remember q="What work was done on authentication?" m=verbose

echo
echo "== Done. Review the outputs above to verify the RAG pipeline (ingest, ask, retrieve, learn, vague, remember, journal). =="
