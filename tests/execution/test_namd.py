# tests/test_namd.py

from pathlib import Path
import pytest
from varidock.execution.namd import get_namd_ns


@pytest.fixture
def make_log(tmp_path):
    def _make(content: str) -> Path:
        log = tmp_path / "test.log"
        log.write_text(content)
        return log

    return _make


def test_returns_none_for_missing_file(tmp_path):
    assert get_namd_ns(tmp_path / "nonexistent.log") is None


def test_returns_none_for_empty_log(make_log):
    assert get_namd_ns(make_log("")) is None


def test_returns_none_for_no_velocity_lines(make_log):
    log = make_log("ENERGY: 1000 -1234.5\nENERGY: 2000 -1235.0\n")
    assert get_namd_ns(log) is None


def test_restart_step_not_complete(make_log):
    log = make_log("WRITING VELOCITIES TO RESTART FILE AT STEP 500000\n")
    ns, complete = get_namd_ns(log)
    assert ns == pytest.approx(1.0)
    assert complete is False


def test_output_step_is_complete(make_log):
    log = make_log("WRITING VELOCITIES TO OUTPUT FILE AT STEP 250000\n")
    ns, complete = get_namd_ns(log)
    assert ns == pytest.approx(0.5)
    assert complete is True


def test_uses_last_step(make_log):
    log = make_log(
        "WRITING VELOCITIES TO RESTART FILE AT STEP 100000\n"
        "WRITING VELOCITIES TO RESTART FILE AT STEP 200000\n"
        "WRITING VELOCITIES TO RESTART FILE AT STEP 300000\n"
    )
    ns, complete = get_namd_ns(log)
    assert ns == pytest.approx(0.6)
    assert complete is False


def test_custom_timestep(make_log):
    log = make_log("WRITING VELOCITIES TO RESTART FILE AT STEP 500000\n")
    ns, complete = get_namd_ns(log, timestep_fs=1.0)
    assert ns == pytest.approx(0.5)
    assert complete is False


def test_mixed_lines(make_log):
    log = make_log(
        "ENERGY: 1000 -1234.5\n"
        "WRITING VELOCITIES TO RESTART FILE AT STEP 100000\n"
        "ENERGY: 2000 -1235.0\n"
        "WRITING VELOCITIES TO OUTPUT FILE AT STEP 250000\n"
        "ENERGY: 3000 -1236.0\n"
    )
    ns, complete = get_namd_ns(log)
    assert ns == pytest.approx(0.5)
    assert complete is True


def test_restart_after_output_not_complete(make_log):
    log = make_log(
        "WRITING VELOCITIES TO OUTPUT FILE AT STEP 100000\n"
        "WRITING VELOCITIES TO RESTART FILE AT STEP 200000\n"
    )
    ns, complete = get_namd_ns(log)
    assert ns == pytest.approx(0.4)
    assert complete is False


def test_output_is_last_line_complete(make_log):
    log = make_log(
        "WRITING VELOCITIES TO RESTART FILE AT STEP 100000\n"
        "WRITING VELOCITIES TO OUTPUT FILE AT STEP 200000\n"
    )
    ns, complete = get_namd_ns(log)
    assert ns == pytest.approx(0.4)
    assert complete is True
