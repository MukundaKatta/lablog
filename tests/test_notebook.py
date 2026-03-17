"""Tests for notebook module: entries, experiments, and protocols."""

import tempfile
from pathlib import Path

from lablog.models import EntryStatus, ExperimentStatus
from lablog.notebook.entry import LabEntryManager
from lablog.notebook.experiment import ExperimentTracker
from lablog.notebook.protocol import ProtocolTemplate


class TestLabEntryManager:
    def setup_method(self):
        self._tmpdir = tempfile.mkdtemp()
        self.mgr = LabEntryManager(storage_dir=self._tmpdir)

    def test_create_and_get(self):
        entry = self.mgr.create(title="Test", hypothesis="H1")
        assert self.mgr.count == 1
        fetched = self.mgr.get(entry.id)
        assert fetched is not None
        assert fetched.title == "Test"

    def test_update(self):
        entry = self.mgr.create(title="Original")
        updated = self.mgr.update(entry.id, title="Updated", results="R1")
        assert updated is not None
        assert updated.title == "Updated"
        assert updated.results == "R1"

    def test_delete(self):
        entry = self.mgr.create(title="To Delete")
        assert self.mgr.delete(entry.id)
        assert self.mgr.get(entry.id) is None
        assert self.mgr.count == 0

    def test_list_entries_by_status(self):
        self.mgr.create(title="Draft")
        e2 = self.mgr.create(title="Completed")
        self.mgr.update(e2.id, status=EntryStatus.COMPLETED)
        drafts = self.mgr.list_entries(status=EntryStatus.DRAFT)
        assert len(drafts) == 1
        assert drafts[0].title == "Draft"

    def test_list_entries_by_tags(self):
        self.mgr.create(title="Bio", tags=["biology"])
        self.mgr.create(title="Chem", tags=["chemistry"])
        results = self.mgr.list_entries(tags=["biology"])
        assert len(results) == 1
        assert results[0].title == "Bio"

    def test_search_by_title(self):
        self.mgr.create(title="Cell Growth Assay")
        self.mgr.create(title="Protein Binding")
        results = self.mgr.search_by_title("cell")
        assert len(results) == 1

    def test_persistence(self):
        entry = self.mgr.create(title="Persistent")
        # Create new manager pointing to same directory
        mgr2 = LabEntryManager(storage_dir=self._tmpdir)
        fetched = mgr2.get(entry.id)
        assert fetched is not None
        assert fetched.title == "Persistent"


class TestExperimentTracker:
    def setup_method(self):
        self._tmpdir = tempfile.mkdtemp()
        self.tracker = ExperimentTracker(storage_dir=self._tmpdir)

    def test_create_and_get(self):
        exp = self.tracker.create(name="exp-001", parameters={"temp": 37})
        assert self.tracker.count == 1
        fetched = self.tracker.get(exp.id)
        assert fetched is not None
        assert fetched.parameters["temp"] == 37

    def test_lifecycle(self):
        exp = self.tracker.create(name="lifecycle")
        assert exp.status == ExperimentStatus.PLANNED

        self.tracker.start(exp.id)
        exp = self.tracker.get(exp.id)
        assert exp.status == ExperimentStatus.RUNNING
        assert exp.started_at is not None

        self.tracker.complete(exp.id)
        exp = self.tracker.get(exp.id)
        assert exp.status == ExperimentStatus.COMPLETED
        assert exp.completed_at is not None

    def test_fail(self):
        exp = self.tracker.create(name="failing")
        self.tracker.start(exp.id)
        self.tracker.fail(exp.id)
        exp = self.tracker.get(exp.id)
        assert exp.status == ExperimentStatus.FAILED

    def test_log_metric(self):
        exp = self.tracker.create(name="metric-test")
        self.tracker.log_metric(exp.id, "accuracy", 0.95, unit="%")
        self.tracker.log_metric(exp.id, "accuracy", 0.97, unit="%")
        exp = self.tracker.get(exp.id)
        assert len(exp.metrics) == 2

    def test_add_artifact(self):
        exp = self.tracker.create(name="artifact-test")
        assert self.tracker.add_artifact(exp.id, "plot", "/tmp/p.png", "image")
        exp = self.tracker.get(exp.id)
        assert len(exp.artifacts) == 1

    def test_compare_experiments(self):
        e1 = self.tracker.create(name="A")
        e2 = self.tracker.create(name="B")
        self.tracker.log_metric(e1.id, "score", 0.8)
        self.tracker.log_metric(e2.id, "score", 0.9)
        comparison = self.tracker.compare_experiments([e1.id, e2.id], "score")
        assert "A" in comparison
        assert comparison["B"] == [0.9]


class TestProtocolTemplate:
    def setup_method(self):
        self._tmpdir = tempfile.mkdtemp()
        self.pt = ProtocolTemplate(storage_dir=self._tmpdir)

    def test_create_and_get(self):
        protocol = self.pt.create(
            name="PCR",
            steps=[{"instruction": "Denature", "duration_minutes": 5}],
            required_materials=["primers"],
        )
        assert self.pt.count == 1
        fetched = self.pt.get(protocol.id)
        assert fetched.name == "PCR"
        assert len(fetched.steps) == 1

    def test_add_step(self):
        protocol = self.pt.create(name="Multi-step")
        self.pt.add_step(protocol.id, "Step 1", duration_minutes=10)
        self.pt.add_step(protocol.id, "Step 2", duration_minutes=5)
        p = self.pt.get(protocol.id)
        assert len(p.steps) == 2
        assert p.steps[0].order == 1
        assert p.steps[1].order == 2

    def test_delete(self):
        protocol = self.pt.create(name="Deletable")
        assert self.pt.delete(protocol.id)
        assert self.pt.count == 0

    def test_instantiate_experiment(self):
        protocol = self.pt.create(
            name="Standard Assay",
            steps=[{"instruction": "Prepare"}],
            required_materials=["buffer"],
            tags=["assay"],
        )
        exp = self.pt.instantiate_experiment(protocol.id, "assay-run-1", concentration=10)
        assert exp is not None
        assert exp.name == "assay-run-1"
        assert exp.parameters["protocol_name"] == "Standard Assay"
        assert exp.parameters["concentration"] == 10
        assert "assay" in exp.tags
