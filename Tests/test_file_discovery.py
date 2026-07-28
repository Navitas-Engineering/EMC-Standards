from pathlib import Path

from extraction import get_file_names


def create_mock_pdf(path):
    """
    Create an empty file with a PDF extension.

    File discovery checks paths and extensions only, so the file
    does not need to contain valid PDF data.
    """

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    path.touch()


def resolved_paths(paths):
    return {
        Path(path).resolve()
        for path in paths
    }


def test_get_file_names_finds_pdf_files(tmp_path):
    target_directory = tmp_path / "Target"

    first_pdf = (
        target_directory
        / "standard-one.pdf"
    )

    second_pdf = (
        target_directory
        / "Subfolder"
        / "standard-two.PDF"
    )

    create_mock_pdf(first_pdf)
    create_mock_pdf(second_pdf)

    discovered = get_file_names(
        target_directory
    )

    discovered_paths = resolved_paths(
        discovered
    )

    assert first_pdf.resolve() in discovered_paths
    assert second_pdf.resolve() in discovered_paths


def test_get_file_names_ignores_non_pdf_files(tmp_path):
    target_directory = tmp_path / "Target"

    pdf_file = (
        target_directory
        / "standard.pdf"
    )

    text_file = (
        target_directory
        / "notes.txt"
    )

    create_mock_pdf(pdf_file)

    text_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    text_file.write_text(
        "Not a PDF",
        encoding="utf-8"
    )

    discovered = get_file_names(
        target_directory
    )

    discovered_paths = resolved_paths(
        discovered
    )

    assert pdf_file.resolve() in discovered_paths
    assert text_file.resolve() not in discovered_paths


def test_get_file_names_excludes_configured_rejected_folder(
    tmp_path
):
    target_directory = tmp_path / "Target"
    rejected_directory = target_directory / "Rejected"

    active_pdf = (
        target_directory
        / "active.pdf"
    )

    rejected_pdf = (
        rejected_directory
        / "rejected.pdf"
    )

    create_mock_pdf(active_pdf)
    create_mock_pdf(rejected_pdf)

    discovered = get_file_names(
        directory=target_directory,
        rejected_directory=rejected_directory
    )

    discovered_paths = resolved_paths(
        discovered
    )

    assert active_pdf.resolve() in discovered_paths
    assert rejected_pdf.resolve() not in discovered_paths


def test_get_file_names_continues_to_scan_hold_folder(
    tmp_path
):
    target_directory = tmp_path / "Target"
    rejected_directory = target_directory / "Rejected"
    hold_directory = target_directory / "Hold"

    held_pdf = (
        hold_directory
        / "awaiting-clarification.pdf"
    )

    rejected_pdf = (
        rejected_directory
        / "not-a-standard.pdf"
    )

    create_mock_pdf(held_pdf)
    create_mock_pdf(rejected_pdf)

    discovered = get_file_names(
        directory=target_directory,
        rejected_directory=rejected_directory
    )

    discovered_paths = resolved_paths(
        discovered
    )

    assert held_pdf.resolve() in discovered_paths
    assert rejected_pdf.resolve() not in discovered_paths


def test_only_configured_rejected_directory_is_excluded(
    tmp_path
):
    target_directory = tmp_path / "Target"

    configured_rejected_directory = (
        target_directory
        / "Rejected"
    )

    unrelated_rejected_directory = (
        target_directory
        / "Project Archive"
        / "Rejected"
    )

    configured_rejected_pdf = (
        configured_rejected_directory
        / "excluded.pdf"
    )

    unrelated_pdf = (
        unrelated_rejected_directory
        / "still-discovered.pdf"
    )

    create_mock_pdf(configured_rejected_pdf)
    create_mock_pdf(unrelated_pdf)

    discovered = get_file_names(
        directory=target_directory,
        rejected_directory=configured_rejected_directory
    )

    discovered_paths = resolved_paths(
        discovered
    )

    assert (
        configured_rejected_pdf.resolve()
        not in discovered_paths
    )

    assert unrelated_pdf.resolve() in discovered_paths