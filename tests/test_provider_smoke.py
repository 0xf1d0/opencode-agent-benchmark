"""Conservative owner statements stay separate from formal qualification."""

import json
from pathlib import Path
import unittest

from scripts.create_workspace import REPOSITORY_ROOT
from scripts.runtime_lock import validate_schema


SELECTED = {
    "albert": "qwen3-coder-30b-a3b-instruct",
    "aristote": "qwen-3.6-35b-instruct",
    "mistral": "codestral-2508",
    "nvidia": "nvidia/nemotron-3.5-lightning-30b-a3b",
}


def metadata(provider):
    return json.loads((REPOSITORY_ROOT / "providers" / provider / "metadata.json").read_bytes())


class ProviderSmokeTests(unittest.TestCase):
    def test_common_cell_vocabulary_does_not_promote_smoke_or_guess_other_cells(self):
        for provider, selected in SELECTED.items():
            m = metadata(provider)
            q = m["qualification"]
            self.assertEqual(m["default_model_id"], selected)
            self.assertEqual(q["first_preflight_model_id"], selected)
            self.assertEqual(q["status"], "restricted_smoke_observed")
            self.assertEqual(q["status_scope"], "first_preflight_model_id_only")
            self.assertEqual(set(q["model_states"]), {c["model_id"] for c in m["configs"].values()})
            self.assertFalse(q["formal_preflight_qualified"])
            self.assertFalse(q["scored_ready"])
            self.assertIsNone(q["preflight_record"])
            for model_id, state in q["model_states"].items():
                self.assertEqual(set(state), {"catalog_qualified", "inference_observed", "restricted_smoke_observed", "formal_preflight_qualified", "scored_ready", "status"})
                self.assertTrue(state["catalog_qualified"])
                self.assertFalse(state["formal_preflight_qualified"])
                self.assertFalse(state["scored_ready"])
                if model_id == selected:
                    self.assertTrue(state["inference_observed"])
                    self.assertTrue(state["restricted_smoke_observed"])
                else:
                    self.assertEqual(state["status"], "catalog_qualified")
                    self.assertIsNone(state["restricted_smoke_observed"])
                    if provider != "mistral":
                        self.assertIsNone(state["inference_observed"])

    def test_rate_limited_models_remain_candidates_with_no_inferred_unavailability(self):
        m = metadata("mistral")
        probes = {p["model_id"]: p for p in m["qualification"]["owner_api_probes"]}
        self.assertEqual(set(probes), {"mistral-medium-3-5", "mistral-small-2603", "codestral-2508"})
        for model_id in ("mistral-medium-3-5", "mistral-small-2603"):
            p = probes[model_id]
            self.assertTrue(p["catalog_visible"])
            self.assertTrue(p["inference_probe_attempted"])
            self.assertEqual(p["inference_result"], "rate_limited")
            self.assertEqual(p["http_status"], 429)
            self.assertEqual(p["provider_error"], "Rate limit exceeded")
            self.assertEqual(p["provider_error_code"], 1300)
            self.assertFalse(p["inference_qualified_at_smoke_level"])
            self.assertIsNone(p["unavailable"])
            self.assertIsNone(p["rate_limit_cause"])
            self.assertIn(model_id, {c["model_id"] for c in m["configs"].values()})
            self.assertFalse(m["qualification"]["model_states"][model_id]["inference_observed"])
        success = probes["codestral-2508"]
        self.assertEqual(success["http_status"], 200)
        self.assertEqual(success["response_model_id"], "codestral-2508")
        self.assertEqual(success["response_content"], "ACCESS_OK")
        self.assertTrue(success["direct_api_inference_observed"])
        self.assertTrue(success["inference_qualified_at_smoke_level"])
        for p in probes.values():
            self.assertIsNone(p["observed_at"])
            self.assertIsNone(p["evidence_sha256"])

    def test_codestral_exact_smoke_prompts_and_observations_have_no_routing_or_file_hash_claim(self):
        q = metadata("mistral")["qualification"]
        o = q["owner_observation"]
        self.assertEqual(o["model_id"], "codestral-2508")
        self.assertEqual(o["shell_probe_status"], "restricted_shell_execution_not_observed")
        probes = o["probes"]
        self.assertEqual(probes[0]["prompt"], "Réponds uniquement par PREFLIGHT_OK.")
        self.assertEqual(probes[0]["response"], "PREFLIGHT_OK")
        self.assertEqual(probes[0]["displayed_label"], "Build · codestral-2508")
        self.assertEqual(probes[1]["reported_written_file"], "preflight_probe.txt")
        self.assertEqual(probes[1]["displayed_content"], "PREFLIGHT_FILE_OK")
        self.assertIsNone(probes[1]["external_file_sha256"])
        self.assertIsNone(probes[1]["external_filesystem_audit"])
        self.assertFalse(probes[2]["shell_tool_execution_observed"])
        self.assertFalse(probes[2]["shell_stdout_observed"])
        manual = (REPOSITORY_ROOT / "docs/preflight-mistral.md").read_text()
        for p in probes:
            self.assertIn(p["prompt"], manual)

    def test_nvidia_ambiguous_text_is_not_a_confirmed_bypass(self):
        o = metadata("nvidia")["qualification"]["owner_observation"]
        ambiguous = o["earlier_ambiguous_shell_request"]
        self.assertIsNone(ambiguous["prompt"])
        self.assertIsNone(ambiguous["shell_tool_execution_observed"])
        self.assertIsNone(ambiguous["confirmed_permission_bypass"])
        explicit = o["explicit_shell_probe"]
        self.assertEqual(explicit["prompt"], metadata("mistral")["qualification"]["owner_observation"]["probes"][2]["prompt"])
        self.assertFalse(explicit["shell_tool_execution_observed"])
        self.assertFalse(explicit["shell_stdout_observed"])
        self.assertEqual(o["shell_probe_status"], "restricted_shell_execution_not_observed")
        self.assertIsNone(o["trivial_inference"])
        self.assertIsNone(o["file_creation"])
        self.assertIsNone(metadata("albert")["qualification"]["owner_observation"]["shell_probe_status"])
        self.assertEqual(metadata("aristote")["qualification"]["owner_observation"]["shell_probe_status"], "restricted_shell_execution_not_observed")

    def test_observations_keep_missing_evidence_null_and_all_formal_templates_blank(self):
        for provider, model_id in SELECTED.items():
            o = metadata(provider)["qualification"]["owner_observation"]
            for field in ("observed_at", "evidence_sha256", "runtime_lock_sha256", "effective_configuration_sha256", "routing_proof", "opencode_version"):
                self.assertIsNone(o[field], (provider, field))
            self.assertFalse(o["formal_preflight_complete"])
            self.assertFalse(o["scored_ready"])
            record = json.loads((REPOSITORY_ROOT / "runtime" / f"preflight.{provider}.example.json").read_bytes())
            validate_schema(record, "preflight.schema.json")
            self.assertEqual(record["model_id"], model_id)
            self.assertFalse(record["scored_ready"])
            self.assertIsNone(record["runtime_lock_sha256"])
            self.assertIsNone(record["os_boundary_verified"])
            self.assertIsNone(record["effective_configuration_sha256"])
            for check in record["checks"].values():
                self.assertEqual(check["status"], "not_run")
                self.assertIsNone(check["observed_at"])
                self.assertIsNone(check["evidence_sha256"])
