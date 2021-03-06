from os import environ
import pytest

from citrination_client import *
from citrination_client.search.client import MAX_QUERY_DEPTH
from citrination_client.base.errors import CitrinationClientError


class TestPifQuery():
    @classmethod
    def setup_class(cls):
        cls.client = CitrinationClient().search

    @pytest.mark.skipif(environ['CITRINATION_SITE'] != "https://citrination.com",
                        reason="Test only supported on public")
    def test_uid_query(self):
        """Testing that a query against a UID only pulls back that record"""
        target_uid = "000496A81BDD616A5BBA1FC4D3B5AC1A"
        query = PifSystemReturningQuery(query=DataQuery(system=PifSystemQuery(uid=Filter(equal=target_uid))))
        result = self.client.pif_search(query)
        assert result.total_num_hits == 1
        assert result.hits[0].system.uid == target_uid

    @pytest.mark.skipif(environ['CITRINATION_SITE'] != "https://citrination.com",
                        reason="Test only supported on public")
    def test_pagination_overflow(self):
        """
        Tests that if pagination controls (size and from) request a set of
        results that would overflow the end of the results set, all the results
        up to the end of the set are returned
        """
        query = PifSystemReturningQuery(size=0,
                                        query=DataQuery(
                                            dataset=DatasetQuery(
                                                id=Filter(equal='1160'))))
        response = self.client.pif_search(query)
        total = response.total_num_hits
        from_index = total - 20

        query = PifSystemReturningQuery(size=45,
                                        from_index=from_index,
                                        query=DataQuery(
                                            dataset=DatasetQuery(
                                                id=Filter(equal='1160'))))
        response = self.client.pif_search(query)
        assert 20 == len(response.hits)

    def test_search_limit_enforced_pif_search(self):
        """
        Tests that if a user tries to access more than the max allowed results an error is thrown
        """
        query = PifSystemReturningQuery(from_index=MAX_QUERY_DEPTH, size=10)
        with pytest.raises(CitrinationClientError):
            self.client.pif_search(query)

    def test_pagination_from_start(self):
        """
        Tests that pagination works with no from value
        """
        query = PifSystemReturningQuery(size=200)
        response = self.client.pif_search(query)
        assert 200 == len(response.hits)

    def test_pagination_with_from_index(self):
        """
        Test that basic queries with both size and from return results
        """
        query = PifSystemReturningQuery(size=200, from_index=1000)
        response = self.client.pif_search(query)
        assert 200 == len(response.hits)

    def test_auto_pagination(self):
        """
        Tests that, given no pagination control (size nor from), the number of hits is equal to the total_num_hits
        """
        query = PifSystemReturningQuery(
            query=DataQuery(
                dataset=DatasetQuery(
                    id=Filter(equal='150670'))))
        response = self.client.pif_search(query)
        assert response.total_num_hits == len(response.hits)

    @pytest.mark.skipif(environ['CITRINATION_SITE'] != "https://citrination.com",
                        reason="Test only supported on public")
    def test_pif_search(self):
        """
        Tests that a PIF search query can be executed
        """
        response = self.client.pif_search(PifSystemReturningQuery(
            size=0,
            query=DataQuery(
                dataset=DatasetQuery(
                    id=Filter(equal='151278')
                ),
                system=PifSystemQuery(
                    chemical_formula=ChemicalFieldQuery(
                        filter=ChemicalFilter(
                            equal='C22H15NSSi'))))))
        assert 5 == response.total_num_hits

    @pytest.mark.skipif(environ['CITRINATION_SITE'] != "https://citrination.com",
                        reason="Test only supported on public")
    def test_pif_simple_search(self):
        """
        Tests that a simple pif search query can be executed
        """
        response = self.client.pif_search(PifSystemReturningQuery(
            size=0,
            query=DataQuery(
                dataset=DatasetQuery(
                    id=Filter(equal='151278')
                ),
                simple='C22H15NSSi')))
        assert 5 == response.total_num_hits

    @pytest.mark.skipif(environ['CITRINATION_SITE'] != "https://citrination.com",
                        reason="Test only supported on public")
    def test_extracted(self):
        """
        Tests that values are extracted according to the extract_as properties
        of the input query
        """
        response = self.client.pif_search(PifSystemReturningQuery(
            size=1,
            query=DataQuery(
                dataset=DatasetQuery(
                    id=Filter(equal='151278')
                ),
                system=PifSystemQuery(
                    chemical_formula=ChemicalFieldQuery(
                        extract_as='Chemical formula',
                        filter=ChemicalFilter(
                            equal='C22H15NSSi'))))))
        assert response.hits[0].extracted['Chemical formula'] == '$\\rm$C$_{22}$$\\rm$H$_{15}$$\\rm$N$\\rm$S$\\rm$Si'
        assert response.hits[0].extracted_path['Chemical formula'] == '/chemicalFormula'

    def test_updated_at(self):
        """
        Tests that the updated_at filter functions correctly
        """
        all_response = self.client.pif_search(PifSystemReturningQuery(size=1))
        subset_response = self.client.pif_search(PifSystemReturningQuery(
            size=0,
            query=DataQuery(
                system=PifSystemQuery(
                    updated_at=Filter(
                        max='2017-10-01T00:00:00.000Z')))))
        assert all_response.hits[0].updated_at is not None
        assert all_response.total_num_hits != subset_response.total_num_hits

    def test_search_weight(self):
        # Run a query to get a record with a name
        reference_hit = self.client.pif_search(PifSystemReturningQuery(
            size=1,
            return_system=False,
            query=DataQuery(
                system=PifSystemQuery(
                    names=FieldQuery(
                        filter=Filter(exists=True)))))
        ).hits[0]
        uid = reference_hit.id.split('/')[2]

        # Run two queries where everything is the same except the weight on the name query
        search_result = self.client.pif_multi_search(MultiQuery(
            queries=[
                PifSystemReturningQuery(
                    return_system=False,
                    score_relevance=True,
                    query=DataQuery(
                        system=PifSystemQuery(
                            uid=Filter(equal=uid),
                            names=FieldQuery(
                                filter=Filter(exists=True))))),
                PifSystemReturningQuery(
                    return_system=False,
                    score_relevance=True,
                    query=DataQuery(
                        system=PifSystemQuery(
                            uid=Filter(equal=uid),
                            names=FieldQuery(
                                weight=2.0,
                                filter=Filter(exists=True)))))
            ]))

        # Make sure that the two weights are off by the correct amount
        unweighted_score = search_result.results[0].result.hits[0].score
        weighted_score = search_result.results[1].result.hits[0].score
        assert abs(weighted_score - unweighted_score) > 0.01

    def test_simple_search_weight(self):
        # Run a query to get a record with a name
        reference_hit = self.client.pif_search(PifSystemReturningQuery(
            size=1,
            return_system=True,
            query=DataQuery(
                system=PifSystemQuery(
                    names=FieldQuery(
                        filter=Filter(exists=True)))))
        ).hits[0]
        uid = reference_hit.id.split('/')[2]

        # Run two queries where everything is the same except the weight on the name query
        search_result = self.client.pif_multi_search(MultiQuery(
            queries=[
                PifSystemReturningQuery(
                    return_system=False,
                    score_relevance=True,
                    query=DataQuery(
                        system=PifSystemQuery(
                            uid=Filter(equal=uid)),
                        simple=reference_hit.system.names[0])),
                PifSystemReturningQuery(
                    return_system=False,
                    score_relevance=True,
                    query=DataQuery(
                        system=PifSystemQuery(
                            uid=Filter(equal=uid)),
                        simple=reference_hit.system.names[0],
                        simple_weight={'system.names': 2.0}))
            ]))

        # Make sure that the two weights are off by the correct amount
        unweighted_score = search_result.results[0].result.hits[0].score
        weighted_score = search_result.results[1].result.hits[0].score
        assert abs(weighted_score - unweighted_score) > 0.01

    def test_simple_query_generation(self):
        """
        Tests that a query can be generated with the simple query generation helper method
        """
        query = self.client.generate_simple_chemical_query(
                                                    include_datasets=["1160"],
                                                    chemical_formula="CoSi",
                                                    property_name="Band gap",
                                                    property_min=0.0,
                                                    property_max=0.5
                                                )

        response = self.client.pif_search(query)
        assert 1 == response.total_num_hits
