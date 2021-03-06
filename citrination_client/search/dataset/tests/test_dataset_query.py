from os import environ
import unittest
import pytest

from citrination_client import *
from citrination_client.search.client import MAX_QUERY_DEPTH
from citrination_client.base.errors import CitrinationClientError


class TestDatasetQuery(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        cls.client = CitrinationClient(environ['CITRINATION_API_KEY'], environ['CITRINATION_SITE']).search

    @pytest.mark.skipif(environ['CITRINATION_SITE'] != "https://citrination.com",
                        reason="Dataset search test only supported on public")
    def test_full_dataset_query(self):
        """Test a public dataset query with every option on"""
        query = DatasetReturningQuery(
            size=8,
            score_relevance=True,
            count_pifs=True)
        result = self.client.dataset_search(query)

        assert len(result.hits) == 8, "Number of hits didn't match query size"
        assert result.took > 0, "Result shouldn't have been instant"
        assert result.total_num_hits > 10000, "The number of results is too low"
        for hit in result.hits:
            assert len(hit.id) > 0, "Returned empty id"
            assert len(hit.name) > 0, "Returned empty name"
            assert len(hit.email) > 0, "Returned empty email"
            assert hit.num_pifs >= 0, "Dataset had no pifs"
            assert hit.score is not None, "Score is not returned"

    @pytest.mark.skipif(environ['CITRINATION_SITE'] != "https://citrination.com",
                        reason="Dataset search test only supported on public")
    def test_dataset_search(self):
        """Test that a basic query with a dataset ID returns 1 hit"""
        response = self.client.dataset_search(DatasetReturningQuery(
            size=0,
            query=DataQuery(
                dataset=DatasetQuery(
                    id=Filter(equal='151278')))))
        assert 1 == response.total_num_hits

    def test_search_limit_enforced_dataset_search(self):
        """
        Tests that if a user tries to access more than the max allowed results an error is thrown
        """
        query = DatasetReturningQuery(from_index=MAX_QUERY_DEPTH, size=10)
        with pytest.raises(CitrinationClientError):
            self.client.dataset_search(query)

    def test_timeout(self):
        """Test that timeouts are sent properly. This request should fail with an exception."""
        with self.assertRaises(RequestTimeoutException):
            self.client.dataset_search(DatasetReturningQuery(timeout=0, size=10))
