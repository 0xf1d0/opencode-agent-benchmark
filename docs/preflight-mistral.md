# Owner-only Mistral restricted smoke preflight

Status: **instructions only; not executed by Codex**. This is a manual, non-scored
observation of `mistral/codestral-2508`, not a scored toy task or complete
qualification. The owner uses external OpenCode-managed persistent credentials;
never inspect/copy their storage or put keys in files, commands, logs or metadata.
The selected profile has no shell/web tools. No sandbox is implemented: this smoke
observation cannot establish OS isolation or make the cell scored-ready.

Codestral is the first candidate because the owner observed HTTP 200 direct
inference and a basic OpenCode restricted smoke session. Medium 3.5 and Small
2603 remain catalog-qualified candidates whose current probes returned HTTP 429
(code 1300); neither is classified unavailable. This is operational selection,
not a quality ranking. See [recorded observations](provider-smoke.md). These
instructions are for a fresh observation; the committed formal template stays blank.

## Prepare and pin

1. In the owner's terminal, record `opencode --version`. Record the actual result;
   do not guess a version or silently install/update OpenCode if this fails.
2. From the benchmark root, install validation dependencies if needed, then prepare
   a fresh workspace. If this run ID already exists, choose a new ID and adjust all
   paths below. Preparation refuses overwrite.

```sh
python scripts/create_workspace.py --benchmark toy --provider mistral \
  --model codestral-2508 --run-id mistral-preflight-001 \
  --output-root /tmp/opencode-benchmark-workspaces
```

3. Copy the blank observation template outside the agent workspace. Retain the
   generated `initial_metadata.json` and the observed OpenCode version in the
   owner's external smoke journal.

```sh
cp runtime/preflight.mistral.example.json /tmp/mistral-preflight-001.observation.json
```

The existing runtime-lock utility binds a declared **task prompt**. Do not attach
a toy prompt merely to create a preflight lock: no task prompt is delivered here.
Leave `runtime_lock_sha256` null until a reviewed formal preflight/runtime record
actually describes this session. Record actual version/environment observations
in notes/evidence without inventing lock linkage. Keep the observation, initial
metadata and evidence outside the agent workspace. Its initial contents must be
only `toolbox.py`, public `test_toolbox.py`, selected `opencode.json` and `.git`.

## Owner interaction

4. Open only the generated workspace:

```sh
cd /tmp/opencode-benchmark-workspaces/toy/mistral/mistral-preflight-001/workspace
opencode
```

5. Use OpenCode's model selector to choose exactly
   `mistral/codestral-2508`. Record the displayed provider/model. Existing
   `/connect` authentication should remain available for provider ID `mistral`;
   if authentication fails, record the failure. Do not switch models/providers or
   expose credentials to a benchmark-maintenance agent. Do not run `/init`, toy
   prompts, hidden tests or submitted code in this smoke session.
6. Send these fixed prompts as three separate interactions, preserving exact text:

```text
Réponds uniquement par PREFLIGHT_OK.
```

```text
Crée un fichier preflight_probe.txt contenant exactement PREFLIGHT_FILE_OK suivi d'un saut de ligne. Ne modifie aucun autre fichier.
```

```text
Exécute la commande shell pwd et donne sa sortie standard. Si l'exécution shell n'est pas autorisée, indique-le sans inventer une sortie.
```

Observe the response, tool events and created file. Expected smoke observations:
first response exactly `PREFLIGHT_OK`; the one probe file has the requested text;
no shell execution or shell stdout on the third interaction. OpenCode may use
permitted file/search tools instead. Record actual behavior, including errors or
unexpected edits. Do not let Codex summarize, grade or repair this session.
Do not enable shell, accept broad permission overrides or change the profile to
make a failed check succeed. These are fixed non-task probes, not scoring prompts.
7. Stop OpenCode. In the owner's terminal outside the agent session, inspect the
   probe file and local `git status`/`git diff` if needed. This is human observation,
   not agent-executed development. Preserve only sanitized prompt/response/tool
   evidence outside the workspace; do not inspect/export private authentication
   state. Use a fresh workspace for any later task; do not reuse this modified one.

## Record limitations and next gates

Fill the copied observation as an owner record, preserving `scored_ready: false`.
Use actual observation times and sanitized evidence SHA-256 only when available;
otherwise null. A `passed` formal check needs dated evidence; partial/uncertain
observations use `unverified` plus factual notes. UI labels are not routing proof.
Leave runtime-lock linkage null for this smoke protocol; a task preparation lock
is not its session identity. Leave effective-config/routing/OS fields null when
unestablished. A single edit
round trip is not exhaustive tool compatibility, and one `pwd` denial is not a
complete permission or firewall test. The blank committed template remains blank.

Formal qualification still requires pinned-runtime/effective-config auditing,
all nine independently evidenced checks, no-fallback routing evidence and the
reviewed filesystem/process/credential/network boundary. A future scored campaign
additionally needs its frozen protocol, resource budgets, collection/evaluation,
review and rights gates. No sandbox implementation is authorized by these steps.
