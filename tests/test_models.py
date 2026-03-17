"""Tests for LABLOG data models."""

from lablog.models import (
    Artifact,
    Dataset,
    EntryStatus,
    Experiment,
    ExperimentStatus,
    LabEntry,
    Metric,
    Protocol,
    ProtocolStep,
)


class TestLabEntry:
    def test_create_default(self):
        entry = LabEntry(title="Test Entry")
        assert entry.title == "Test Entry"
        assert entry.status == EntryStatus.DRAFT
        assert entry.hypothesis == ""
        assert entry.tags == []
        assert entry.id is not None

    def test_create_full(self):
        entry = LabEntry(
            title="Full Entry",
            hypothesis="H1",
            procedure="Step 1",
            observations="Observed X",
            results="Result Y",
            conclusions="Conclude Z",
            tags=["bio", "test"],
        )
        assert entry.hypothesis == "H1"
        assert entry.tags == ["bio", "test"]

    def test_is_complete(self):
        entry = LabEntry(title="Incomplete")
        assert not entry.is_complete()

        complete = LabEntry(
            title="Complete",
            hypothesis="H",
            procedure="P",
            observations="O",
            results="R",
            conclusions="C",
        )
        assert complete.is_complete()

    def test_serialization(self):
        entry = LabEntry(title="Serialize Me", tags=["a"])
        data = entry.model_dump()
        restored = LabEntry.model_validate(data)
        assert restored.title == entry.title
        assert restored.id == entry.id


class TestExperiment:
    def test_create(self):
        exp = Experiment(name="exp-001", parameters={"temp": 37})
        assert exp.name == "exp-001"
        assert exp.parameters["temp"] == 37
        assert exp.status == ExperimentStatus.PLANNED

    def test_log_metric(self):
        exp = Experiment(name="exp-002")
        metric = exp.log_metric("accuracy", 0.95, unit="%")
        assert isinstance(metric, Metric)
        assert len(exp.metrics) == 1
        assert exp.metrics[0].value == 0.95

    def test_add_artifact(self):
        exp = Experiment(name="exp-003")
        artifact = exp.add_artifact("plot", "/tmp/plot.png", "image")
        assert isinstance(artifact, Artifact)
        assert len(exp.artifacts) == 1

    def test_get_metric_values(self):
        exp = Experiment(name="exp-004")
        exp.log_metric("loss", 0.5)
        exp.log_metric("loss", 0.3)
        exp.log_metric("accuracy", 0.9)
        assert exp.get_metric_values("loss") == [0.5, 0.3]
        assert exp.get_metric_values("accuracy") == [0.9]
        assert exp.get_metric_values("missing") == []


class TestProtocol:
    def test_create(self):
        protocol = Protocol(
            name="PCR Protocol",
            steps=[
                ProtocolStep(order=1, instruction="Denature", duration_minutes=5),
                ProtocolStep(order=2, instruction="Anneal", duration_minutes=3),
            ],
            required_materials=["primers", "dNTPs"],
        )
        assert protocol.name == "PCR Protocol"
        assert len(protocol.steps) == 2
        assert protocol.total_duration_minutes == 8

    def test_total_duration_empty(self):
        protocol = Protocol(name="Empty")
        assert protocol.total_duration_minutes == 0


class TestDataset:
    def test_create(self):
        ds = Dataset(
            name="growth-data",
            columns=["time", "od600"],
            row_count=100,
            file_path="/data/growth.csv",
        )
        assert ds.name == "growth-data"
        assert ds.row_count == 100
        assert len(ds.columns) == 2
