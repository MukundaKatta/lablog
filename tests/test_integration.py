"""Integration tests for Lablog."""
from src.core import Lablog

class TestLablog:
    def setup_method(self):
        self.c = Lablog()
    def test_10_ops(self):
        for i in range(10): self.c.process(i=i)
        assert self.c.get_stats()["ops"] == 10
    def test_service_name(self):
        assert self.c.process()["service"] == "lablog"
    def test_different_inputs(self):
        self.c.process(type="a"); self.c.process(type="b")
        assert self.c.get_stats()["ops"] == 2
    def test_config(self):
        c = Lablog(config={"debug": True})
        assert c.config["debug"] is True
    def test_empty_call(self):
        assert self.c.process()["ok"] is True
    def test_large_batch(self):
        for _ in range(100): self.c.process()
        assert self.c.get_stats()["ops"] == 100
