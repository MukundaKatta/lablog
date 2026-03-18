"""Tests for Lablog."""
from src.core import Lablog
def test_init(): assert Lablog().get_stats()["ops"] == 0
def test_op(): c = Lablog(); c.process(x=1); assert c.get_stats()["ops"] == 1
def test_multi(): c = Lablog(); [c.process() for _ in range(5)]; assert c.get_stats()["ops"] == 5
def test_reset(): c = Lablog(); c.process(); c.reset(); assert c.get_stats()["ops"] == 0
def test_service_name(): c = Lablog(); r = c.process(); assert r["service"] == "lablog"
