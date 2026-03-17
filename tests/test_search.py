"""Tests for the search module: indexer and tagger."""

from lablog.models import LabEntry
from lablog.search.indexer import EntryIndexer
from lablog.search.tagger import AutoTagger


class TestEntryIndexer:
    def setup_method(self):
        self.indexer = EntryIndexer()

    def test_add_and_search(self):
        entry = LabEntry(
            title="Cell Growth Under UV",
            hypothesis="UV inhibits growth",
            procedure="Expose cells to UV",
            results="50% reduction",
        )
        self.indexer.add_entry(entry)
        assert self.indexer.indexed_count == 1
        results = self.indexer.search("UV growth")
        assert len(results) == 1
        assert results[0][0].id == entry.id
        assert results[0][1] > 0

    def test_search_ranking(self):
        e1 = LabEntry(title="UV UV UV exposure", hypothesis="UV hypothesis")
        e2 = LabEntry(title="Single UV mention")
        self.indexer.add_entry(e1)
        self.indexer.add_entry(e2)
        results = self.indexer.search("UV")
        assert len(results) == 2
        # e1 should rank higher due to more UV occurrences
        assert results[0][0].id == e1.id

    def test_remove_entry(self):
        entry = LabEntry(title="Removable")
        self.indexer.add_entry(entry)
        self.indexer.remove_entry(entry.id)
        assert self.indexer.indexed_count == 0
        assert self.indexer.search("removable") == []

    def test_reindex(self):
        e1 = LabEntry(title="First")
        e2 = LabEntry(title="Second")
        self.indexer.add_entry(e1)
        self.indexer.reindex([e2])
        assert self.indexer.indexed_count == 1
        assert self.indexer.search("first") == []
        assert len(self.indexer.search("second")) == 1

    def test_empty_search(self):
        assert self.indexer.search("") == []

    def test_vocabulary_size(self):
        entry = LabEntry(title="hello world", hypothesis="foo bar")
        self.indexer.add_entry(entry)
        assert self.indexer.vocabulary_size >= 4

    def test_search_limit(self):
        for i in range(20):
            self.indexer.add_entry(LabEntry(title=f"Entry about cells {i}"))
        results = self.indexer.search("cells", limit=5)
        assert len(results) == 5


class TestAutoTagger:
    def setup_method(self):
        self.tagger = AutoTagger()

    def test_extract_methods(self):
        entry = LabEntry(
            title="PCR amplification",
            procedure="Performed PCR with standard cycling. Used Western blot for validation.",
        )
        methods = self.tagger.extract_methods(entry)
        assert "pcr" in methods
        assert "western blot" in methods

    def test_extract_reagents(self):
        entry = LabEntry(
            title="Buffer test",
            procedure="Dissolved in DMSO. Washed with PBS. Added EDTA to chelate.",
        )
        reagents = self.tagger.extract_reagents(entry)
        assert "dmso" in reagents
        assert "pbs" in reagents
        assert "edta" in reagents

    def test_extract_keywords(self):
        entry = LabEntry(
            title="Cell Growth Analysis",
            hypothesis="Cell growth is affected by temperature",
            observations="Cell growth increased at higher temperature",
        )
        keywords = self.tagger.extract_keywords(entry, top_n=5)
        assert "cell" in keywords
        assert "growth" in keywords
        assert "temperature" in keywords

    def test_auto_tag(self):
        entry = LabEntry(
            title="PCR optimization",
            procedure="Ran PCR with varying annealing temperatures. Used DMSO as additive.",
            results="Optimal annealing at 58C with DMSO",
        )
        tags = self.tagger.auto_tag(entry, max_tags=10)
        assert len(tags) <= 10
        assert "pcr" in tags
        assert "dmso" in tags

    def test_auto_tag_max_limit(self):
        entry = LabEntry(
            title="PCR with Western blot and microscopy",
            procedure="Used DMSO, PBS, EDTA, ethanol, buffer, primer, antibody",
        )
        tags = self.tagger.auto_tag(entry, max_tags=3)
        assert len(tags) <= 3

    def test_extra_patterns(self):
        tagger = AutoTagger(extra_method_patterns=[r"\bcrispr\b"])
        entry = LabEntry(title="CRISPR gene editing experiment")
        methods = tagger.extract_methods(entry)
        assert "crispr" in methods
