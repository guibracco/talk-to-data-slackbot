"""Tests for the Output PII guardrails."""

import pytest

from talk_to_data_slackbot.output.guardrails import (
    REDACTED_PLACEHOLDER,
    apply_output_guardrails,
    contains_pii,
)


class TestApplyOutputGuardrails:
    """Tests for apply_output_guardrails."""

    def test_redacts_email(self):
        """String containing an email is redacted."""
        content = "Contact user@example.com for details."
        result = apply_output_guardrails(content)
        assert "user@example.com" not in result
        assert REDACTED_PLACEHOLDER in result
        assert result == f"Contact {REDACTED_PLACEHOLDER} for details."

    def test_redacts_phone_us_format(self):
        """String containing a US phone number is redacted."""
        content = "Call 555-123-4567 or (555) 987-6543."
        result = apply_output_guardrails(content)
        assert "555-123-4567" not in result
        assert "(555) 987-6543" not in result
        assert result.count(REDACTED_PLACEHOLDER) == 2

    def test_redacts_phone_international_format(self):
        """String containing +1-555-123-4567 is redacted."""
        content = "Dial +1-555-123-4567 for support."
        result = apply_output_guardrails(content)
        assert "+1-555-123-4567" not in result
        assert REDACTED_PLACEHOLDER in result

    def test_no_pii_returned_unchanged(self):
        """String with no PII is returned unchanged."""
        content = "The total count is 42 and the average is 3.14."
        result = apply_output_guardrails(content)
        assert result == content

    def test_decimal_numbers_not_redacted(self):
        """Numeric answers (e.g. averages) must not be matched as phone numbers."""
        content = "The average payment amount is 13.627419866708982."
        result = apply_output_guardrails(content)
        assert result == content
        assert REDACTED_PLACEHOLDER not in result

    def test_multiple_pii_all_redacted(self):
        """Multiple PII occurrences are all redacted."""
        content = "Email alice@test.com and bob@test.org; call 555-111-2222."
        result = apply_output_guardrails(content)
        assert "alice@test.com" not in result
        assert "bob@test.org" not in result
        assert "555-111-2222" not in result
        assert result.count(REDACTED_PLACEHOLDER) == 3

    def test_empty_string_returned_unchanged(self):
        """Empty string is returned unchanged."""
        assert apply_output_guardrails("") == ""

    def test_none_or_whitespace_only(self):
        """Empty content is returned as-is (falsy check)."""
        assert apply_output_guardrails("") == ""
        # Only empty string is special-cased; whitespace is not
        result = apply_output_guardrails("   ")
        assert result == "   "


class TestContainsPii:
    """Tests for contains_pii."""

    def test_returns_true_when_email_present(self):
        """contains_pii returns True when email is present."""
        assert contains_pii("Reply to admin@company.com") is True

    def test_returns_true_when_phone_present(self):
        """contains_pii returns True when phone number is present."""
        assert contains_pii("Call 555-123-4567") is True

    def test_returns_false_when_no_pii(self):
        """contains_pii returns False when no PII is present."""
        assert contains_pii("The total is 100.") is False

    def test_returns_false_for_empty_string(self):
        """contains_pii returns False for empty string."""
        assert contains_pii("") is False
