"""Tests hors ligne : ne simulent jamais une preuve AWS."""
import copy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import lab
from redact import redact


class SafetyTests(unittest.TestCase):
    def response(self, code=0, value=None, error=""):
        return subprocess.CompletedProcess([], code, json.dumps(value or {}), error)

    def denied(self, action="GetItem", error="AccessDeniedException"):
        return self.response(254, error=f"An error occurred ({error}) when calling the {action} operation: not authorized")

    def test_real_denial_classification(self):
        self.assertEqual(lab.classify(self.denied(), "get-item", "001", False), "EXPECTED DENY")

    def test_missing_credentials_is_failure(self):
        self.assertEqual(lab.classify(self.response(253, error="Unable to locate credentials"), "get-item", "001", False), "FAIL")

    def test_unrelated_access_denied_is_failure(self):
        self.assertEqual(lab.classify(self.denied("GetCallerIdentity"), "get-item", "001", False), "FAIL")

    def test_validation_or_conditional_failure_is_not_deny(self):
        for error in ("ValidationException", "ConditionalCheckFailedException", "ExpiredTokenException"):
            self.assertEqual(lab.classify(self.denied("UpdateItem", error), "update-item", "001", False), "FAIL")

    def test_returned_secret_or_wrong_item_fails(self):
        self.assertEqual(lab.classify(self.response(value={"Item": lab.item("001")}), "get-item", "001", True), "FAIL")
        self.assertEqual(lab.classify(self.response(value={"Item": lab.public_item("002")}), "get-item", "001", True), "FAIL")

    def test_exact_projection_success(self):
        self.assertEqual(lab.classify(self.response(value={"Item": lab.public_item("001")}), "get-item", "001", True), "PASS")

    def test_scan_must_contain_two_exact_items(self):
        for values, count, expected in [([lab.public_item("001")], 1, "FAIL"),
                                        ([lab.public_item("002"), lab.public_item("001")], 2, "PASS")]:
            self.assertEqual(lab.classify(self.response(value={"Items": values, "Count": count}), "scan", None, True), expected)

    def test_policy_rejects_broadening(self):
        document = json.loads((lab.ROOT / "policies/fgac-leadingkeys.json").read_text())
        lab.validation.validate(document, "leadingkeys", template=True)
        for change in ("scan", "missing_null", "extra_allow", "wrong_key"):
            altered = copy.deepcopy(document)
            if change == "scan":
                altered["Statement"][0]["Action"].append("dynamodb:Scan")
            elif change == "missing_null":
                del altered["Statement"][0]["Condition"]["Null"]["dynamodb:LeadingKeys"]
            elif change == "extra_allow":
                altered["Statement"].append(copy.deepcopy(altered["Statement"][0]))
            else:
                altered["Statement"][0]["Condition"]["ForAllValues:StringEquals"]["dynamodb:LeadingKeys"] = ["002"]
            with self.assertRaises(ValueError):
                lab.validation.validate(altered, "leadingkeys", template=True)

    def test_template_cannot_be_deployed(self):
        document = json.loads((lab.ROOT / "policies/fgac-attributes.json").read_text())
        with self.assertRaises(ValueError):
            lab.validation.validate(document, "attributes")

    def test_cleanup_without_authorization_does_not_call_aws(self):
        with patch.object(lab, "aws") as api:
            with self.assertRaises(lab.Stop):
                lab.cleanup(None)
            api.assert_not_called()

    def test_absent_requires_exact_error(self):
        with patch.object(lab, "aws", return_value=self.denied("DescribeTable")):
            with self.assertRaises(lab.Stop):
                lab.absent("dynamodb", "describe-table", "ResourceNotFoundException")

    def test_isolation_removes_inherited_credentials(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(lab, "PRIVATE", Path(directory) / ".secrets"), patch.dict(os.environ, {"AWS_ACCESS_KEY_ID": "fake", "AWS_ENDPOINT_URL": "https://invalid.example"}):
            env = lab.isolated()
            self.assertNotIn("AWS_ACCESS_KEY_ID", env)
            self.assertNotIn("AWS_ENDPOINT_URL", env)
            self.assertTrue(env["AWS_CONFIG_FILE"].startswith(directory))

    def test_redaction(self):
        account = "1" * 12
        access = "AKIA" + "X" * 16
        text = f'Account {account} Access {access} "SessionToken": "not-a-real-token"'
        safe = redact(text)
        self.assertNotIn(account, safe)
        self.assertNotIn(access, safe)
        self.assertNotIn("not-a-real-token", safe)

    def test_no_cli_query_filter(self):
        for phase in ("initial", "attributes", "leadingkeys"):
            for _, action, key, projection, _ in lab.definitions(phase):
                args = lab.arguments(action, key, projection)
                self.assertNotIn("--query", args)
                if projection == "allowed":
                    self.assertIn("--projection-expression", args)

    def test_missing_pdf_stops_before_aws(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(lab, "PDF", Path(directory) / "absent.pdf"), patch.object(lab, "aws") as api:
            with self.assertRaises(lab.Stop):
                lab.preflight()
            api.assert_not_called()


if __name__ == "__main__":
    unittest.main()
