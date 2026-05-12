import re
from dataclasses import fields
from pathlib import Path

import pytest

from repotrust.finding_catalog import FINDING_REFERENCES
from repotrust.models import (
    JSON_SCHEMA_VERSION,
    Assessment,
    AssessmentProfile,
    DetectedFiles,
    Finding,
    Score,
    Target,
)
from repotrust.reports import FINDING_EXPLANATIONS, FINDING_TITLES


DOCUMENTED_FINDING_ID_RE = re.compile(
    r"(?<![A-Za-z0-9_])"
    r"(?:target|readme|install|security|dependency|hygiene|remote)"
    r"\.[a-z0-9_.]+"
)
SOURCE_FINDING_ID_RE = re.compile(
    r"""["']((?:target|readme|install|security|dependency|hygiene|remote)\.[a-z0-9_.]+)["']"""
)


def test_finding_reference_documents_source_finding_ids():
    reference_path = Path("docs/finding-reference.md")
    if not reference_path.exists():
        pytest.skip("docs/ is intentionally gitignored and may be absent in clean checkouts")

    source_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in Path("src/repotrust").glob("*.py")
    )
    reference_text = reference_path.read_text(encoding="utf-8")

    source_ids = set(SOURCE_FINDING_ID_RE.findall(source_text))
    documented_ids = set(DOCUMENTED_FINDING_ID_RE.findall(reference_text))

    assert source_ids <= documented_ids


def test_finding_catalog_covers_report_explanations_and_titles():
    report_ids = set(FINDING_TITLES) | set(FINDING_EXPLANATIONS)

    assert report_ids <= set(FINDING_REFERENCES)


def test_json_report_reference_documents_model_fields():
    reference_path = Path("docs/json-report-reference.md")
    if not reference_path.exists():
        pytest.skip("docs/ is intentionally gitignored and may be absent in clean checkouts")

    reference_text = reference_path.read_text(encoding="utf-8")

    assert f'`schema_version: "{JSON_SCHEMA_VERSION}"`' in reference_text

    for key in (
        "schema_version",
        "target",
        "detected_files",
        "findings",
        "score",
        "assessment",
        "generated_at",
    ):
        assert f"`{key}`" in reference_text

    for model in (
        Target,
        DetectedFiles,
        Finding,
        Score,
        Assessment,
        AssessmentProfile,
    ):
        for field in fields(model):
            assert f"`{field.name}`" in reference_text

    for profile_key in ("install", "dependency", "agent_delegate"):
        assert f"`{profile_key}`" in reference_text
