from shapely import geometry
import topojson
import geopandas
from topojson.core.join import Join


# the returned hashmap has true for junction points
def test_join_true_for_junction_points():
    data = {
        "cba": {"type": "LineString", "coordinates": [[2, 0], [1, 0], [0, 0]]},
        "ab": {"type": "LineString", "coordinates": [[0, 0], [1, 0]]},
    }
    topo = Join(data).to_dict()

    assert geometry.MultiPoint(topo["junctions"]).equals(
        geometry.MultiPoint([(1.0, 0.0), (0.0, 0.0), (2.0, 0.0)])
    )


# the returned hashmap has undefined for non-junction points
def test_join_undefined_for_non_junction_points():
    data = {
        "cba": {"type": "LineString", "coordinates": [[2, 0], [1, 0], [0, 0]]},
        "ab": {"type": "LineString", "coordinates": [[0, 0], [2, 0]]},
    }
    topo = Join(data).to_dict()

    assert geometry.Point(1.0, 0.0) not in geometry.MultiPoint(topo["junctions"])


# forward backward lines
def test_join_forward_backward_lines():
    data = {
        "foo": {
            "type": "LineString",
            "coordinates": [(0, 0), (10, 0), (10, 5), (20, 5)],
        },
        "bar": {
            "type": "LineString",
            "coordinates": [(5, 0), (30, 0), (30, 5), (0, 5)],
        },
    }
    topo = Join(data).to_dict()

    assert len(topo["junctions"]) == 5


# more than two lines
def test_join_more_than_two_lines():
    data = {
        "foo": {"type": "LineString", "coordinates": [(0, 0), (15, 2.5), (30, 5)]},
        "bar": {"type": "LineString", "coordinates": [(0, 0), (15, 2.5), (30, 5)]},
        "baz": {
            "type": "LineString",
            "coordinates": [(0, 0), (10, 0), (10, 5), (20, 5)],
        },
        "qux": {
            "type": "LineString",
            "coordinates": [(5, 0), (30, 0), (30, 5), (0, 5)],
        },
    }
    topo = Join(data).to_dict()

    assert len(topo["junctions"]) == 5


# exact duplicate lines ABC & ABC have no junctions
def test_join_duplicate_lines_junction_endpoints():
    data = {
        "abc1": {"type": "LineString", "coordinates": [[0, 0], [1, 0], [2, 0]]},
        "abc2": {"type": "LineString", "coordinates": [[0, 0], [1, 0], [2, 0]]},
    }
    topo = Join(data).to_dict()

    assert topo["junctions"] == []


# reversed duplicate lines ABC & CBA have no junctions
def test_join_reversed_duplicate_lines_junction_endpoints():
    data = {
        "abc": {"type": "LineString", "coordinates": [[0, 0], [1, 0], [2, 0]]},
        "cba": {"type": "LineString", "coordinates": [[2, 0], [1, 0], [0, 0]]},
    }
    topo = Join(data).to_dict()

    assert topo["junctions"] == []


# exact duplicate rings ABCA & ABCA have no junctions
def test_join_exact_duplicate_rings():
    data = {
        "abca1": {"type": "Polygon", "coordinates": [[[0, 0], [1, 1], [2, 0], [0, 0]]]},
        "abca2": {"type": "Polygon", "coordinates": [[[0, 0], [1, 1], [2, 0], [0, 0]]]},
    }
    topo = Join(data).to_dict()

    assert topo["junctions"] == []


# reversed duplicate rings ABCA & ACBA have no junctions
def test_join_reversed_duplicate_rings():
    data = {
        "abca": {"type": "Polygon", "coordinates": [[[0, 0], [1, 1], [2, 0], [0, 0]]]},
        "acba": {"type": "Polygon", "coordinates": [[[0, 0], [2, 0], [1, 1], [0, 0]]]},
    }
    topo = Join(data).to_dict()

    assert topo["junctions"] == []


# rotated duplicate rings BCAB & ABCA have no junctions
def test_join_rotated_duplicate_rings():
    data = {
        "abca": {"type": "Polygon", "coordinates": [[[0, 0], [1, 1], [2, 0], [0, 0]]]},
        "bcab": {"type": "Polygon", "coordinates": [[[1, 1], [2, 0], [0, 0], [1, 1]]]},
    }
    topo = Join(data).to_dict()
    assert topo["junctions"] == []


# ring ABCA & line ABCA have no junction at A
def test_join_equal_ring_and_line_no_junctions():
    data = {
        "abcaLine": {
            "type": "LineString",
            "coordinates": [[0, 0], [1, 1], [2, 0], [0, 0]],
        },
        "abcaPolygon": {
            "type": "Polygon",
            "coordinates": [[[0, 0], [1, 1], [2, 0], [0, 0]]],
        },
    }
    topo = Join(data).to_dict()

    assert topo["junctions"] == []


# ring ABCA & line ABCA have no junctions
def test_join_rotated_ring_and_line_no_junctions():
    data = {
        "abcaLine": {
            "type": "LineString",
            "coordinates": [[0, 0], [1, 1], [2, 0], [0, 0]],
        },
        "bcabPolygon": {
            "type": "Polygon",
            "coordinates": [[[1, 1], [2, 0], [0, 0], [1, 1]]],
        },
    }
    topo = Join(data).to_dict()

    assert topo["junctions"] == []


# when an old arc ABC extends a new arc AB, there is a junction at B
def test_join_line_ABC_extends_new_line_AB():
    data = {
        "abc": {"type": "LineString", "coordinates": [[0, 0], [1, 0], [2, 0]]},
        "ab": {"type": "LineString", "coordinates": [[0, 0], [1, 0]]},
    }
    topo = Join(data).to_dict()

    assert geometry.MultiPoint(topo["junctions"]).equals(
        geometry.MultiPoint([(0.0, 0.0), (1.0, 0.0)])
    )


# when a reversed old arc CBA extends a new arc AB, there is a junction at B
def test_join_reversed_line_CBA_extends_new_line_AB():
    data = {
        "cba": {"type": "LineString", "coordinates": [[2, 0], [1, 0], [0, 0]]},
        "ab": {"type": "LineString", "coordinates": [[0, 0], [1, 0]]},
    }
    topo = Join(data).to_dict()

    assert geometry.Point(1.0, 0.0) in geometry.MultiPoint(topo["junctions"])


# when a new arc ADE shares its start with an old arc ABC, there is no junction at A
def test_join_line_ADE_share_starts_with_ABC():
    data = {
        "ade": {"type": "LineString", "coordinates": [[0, 0], [1, 0], [2, 0]]},
        "abc": {"type": "LineString", "coordinates": [[0, 0], [1, 1], [2, 1]]},
    }
    topo = Join(data).to_dict()

    assert topo["junctions"] == []


# ring ABA has no junctions
def test_join_single_ring_ABCA():
    data = {
        "abca": {"type": "LineString", "coordinates": [[0, 0], [1, 0], [1, 1], [0, 0]]}
    }
    topo = Join(data).to_dict()

    assert topo["junctions"] == []


# ring AA is not a proper polygon geometry.
def test_join_single_ring_AA():
    data = {"aa": {"type": "Polygon", "coordinates": [[0, 0], [0, 0]]}}
    topo = Join(data).to_dict()

    assert topo["junctions"] == []


# when a new line DEC shares its end with an old line ABC, there is no junction at C
def test_join_line_DEC_share_line_ABC():
    data = {
        "abc": {"type": "LineString", "coordinates": [[0, 0], [1, 0], [2, 0]]},
        "dec": {"type": "LineString", "coordinates": [[0, 1], [1, 1], [2, 0]]},
    }
    topo = Join(data).to_dict()
    assert topo["junctions"] == []


# when a new line ABC extends an old line AB, there is a junction at B
def test_join_line_ABC_extends_line_AB():
    data = {
        "ab": {"type": "LineString", "coordinates": [[0, 0], [1, 0]]},
        "abc": {"type": "LineString", "coordinates": [[0, 0], [1, 0], [2, 0]]},
    }
    topo = Join(data).to_dict()

    assert geometry.MultiPoint(topo["junctions"]).equals(
        geometry.MultiPoint([(0.0, 0.0), (1.0, 0.0)])
    )


# when a new line ABC extends a reversed old line BA, there is a junction at B
def test_join_line_ABC_extends_line_BA():
    data = {
        "ba": {"type": "LineString", "coordinates": [[1, 0], [0, 0]]},
        "abc": {"type": "LineString", "coordinates": [[0, 0], [1, 0], [2, 0]]},
    }
    topo = Join(data).to_dict()

    assert geometry.MultiPoint(topo["junctions"]).equals(
        geometry.MultiPoint([(1.0, 0.0), (0.0, 0.0)])
    )


# when a new line starts BC in the middle of an old line ABC, there is a
# junction at B
def test_join_line_ABC_extends_line_BC():
    data = {
        "abc": {"type": "LineString", "coordinates": [[0, 0], [1, 0], [2, 0]]},
        "bc": {"type": "LineString", "coordinates": [[1, 0], [2, 0]]},
    }
    topo = Join(data).to_dict()

    assert geometry.MultiPoint(topo["junctions"]).equals(
        geometry.MultiPoint([(1.0, 0.0), (0.0, 0.0), (2.0, 0.0)])
    )


# when a new line BC starts in the middle of a reversed old line CBA, there is a
# junction at B
def test_join_line_BC_start_middle_reversed_line_CBA():
    data = {
        "cba": {"type": "LineString", "coordinates": [[2, 0], [1, 0], [0, 0]]},
        "bc": {"type": "LineString", "coordinates": [[1, 0], [2, 0]]},
    }
    topo = Join(data).to_dict()

    assert geometry.MultiPoint(topo["junctions"]).equals(
        geometry.MultiPoint([(2.0, 0.0), (1.0, 0.0)])
    )


# when a new line ABD deviates from an old line ABC, there is a junction at B
def test_join_line_ABD_deviates_line_ABC():
    data = {
        "abc": {"type": "LineString", "coordinates": [[0, 0], [1, 0], [2, 0]]},
        "abd": {"type": "LineString", "coordinates": [[0, 0], [1, 0], [3, 0]]},
    }
    topo = Join(data).to_dict()

    assert geometry.MultiPoint(topo["junctions"]).equals(
        geometry.MultiPoint([(0.0, 0.0), (2.0, 0.0)])
    )


# when a new line ABD deviates from a reversed old line CBA, there is a
# junction at B
def test_join_line_ABD_deviates_line_CBA():
    data = {
        "cba": {"type": "LineString", "coordinates": [[2, 0], [1, 0], [0, 0]]},
        "abd": {"type": "LineString", "coordinates": [[0, 0], [1, 0], [3, 0]]},
    }
    topo = Join(data).to_dict()

    assert geometry.MultiPoint(topo["junctions"]).equals(
        geometry.MultiPoint([(2.0, 0.0), (0.0, 0.0)])
    )


# when a new line DBC merges into an old line ABC, there is a junction at B
def test_join_line_DBC_merge_line_ABC():
    data = {
        "abc": {"type": "LineString", "coordinates": [[0, 0], [1, 0], [2, 0]]},
        "dbc": {"type": "LineString", "coordinates": [[3, 0], [1, 0], [2, 0]]},
    }
    topo = Join(data).to_dict()

    assert geometry.MultiPoint(topo["junctions"]).equals(
        geometry.MultiPoint([(1.0, 0.0), (2.0, 0.0), (3.0, 0.0), (0.0, 0.0)])
    )


# when a new line DBC merges into a reversed old line CBA, there is a junction at B
def test_join_line_DBC_merge_reversed_line_CBA():
    data = {
        "cba": {"type": "LineString", "coordinates": [[2, 0], [1, 0], [0, 0]]},
        "dbc": {"type": "LineString", "coordinates": [[3, 0], [1, 0], [2, 0]]},
    }
    topo = Join(data).to_dict()

    assert geometry.MultiPoint(topo["junctions"]).equals(
        geometry.MultiPoint([(2.0, 0.0), (1.0, 0.0), (3.0, 0.0)])
    )


# when a new line DBE shares a single midpoint with an old line ABC, there is
# no junction at B
def test_join_line_DBE_share_singe_midpoint_line_ABC():
    data = {
        "abc": {"type": "LineString", "coordinates": [[0, 0], [1, 0], [2, 0]]},
        "dbe": {"type": "LineString", "coordinates": [[0, 1], [1, 0], [2, 1]]},
    }
    topo = Join(data).to_dict()
    assert topo["junctions"] == []


# when a new line ABDE skips a point with an old line ABCDE, there is a no junction
def test_join_line_ABDE_skips_point_line_ABCDE():
    data = {
        "abcde": {
            "type": "LineString",
            "coordinates": [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0]],
        },
        "abde": {"type": "LineString", "coordinates": [[0, 0], [1, 0], [3, 0], [4, 0]]},
    }
    topo = Join(data).to_dict()
    assert topo["junctions"] == []


# when a new line ABDE skips a point with a reversed old line EDCBA, there is
# no junction
def test_join_line_ABDE_skips_point_reversed_line_EDCBA():
    data = {
        "edcba": {
            "type": "LineString",
            "coordinates": [[4, 0], [3, 0], [2, 0], [1, 0], [0, 0]],
        },
        "abde": {"type": "LineString", "coordinates": [[0, 0], [1, 0], [3, 0], [4, 0]]},
    }
    topo = Join(data).to_dict()
    assert topo["junctions"] == []


# when a line ABCDBE self-intersects with its middle, there are no junctions
def test_join_line_ABCDBE_self_intersects_with_middle():
    data = {
        "abcdbe": {
            "type": "LineString",
            "coordinates": [[0, 0], [1, 0], [2, 0], [3, 0], [1, 0], [4, 0]],
        }
    }
    topo = Join(data).to_dict()

    assert topo["junctions"] == []


# when a line ABACD self-intersects with its start, there are no junctions
def test_join_line_ABACD_self_intersects_with_middle():
    data = {
        "abacd": {
            "type": "LineString",
            "coordinates": [[0, 0], [1, 0], [0, 0], [3, 0], [4, 0]],
        }
    }
    topo = Join(data).to_dict()

    assert topo["junctions"] == []


# when a line ABCDBD self-intersects with its end, there are no junctions
def test_join_line_ABCDBD_self_intersects_with_end():
    data = {
        "abcdbd": {
            "type": "LineString",
            "coordinates": [[0, 0], [1, 0], [4, 0], [3, 0], [4, 0]],
        }
    }
    topo = Join(data).to_dict()

    assert topo["junctions"] == []


# when an old line ABCDBE self-intersects and shares a point B, there is
# no junction at B
def test_join_line_ABCDB_self_intersects():
    data = {
        "abcdbe": {
            "type": "LineString",
            "coordinates": [[0, 0], [1, 0], [2, 0], [3, 0], [1, 0], [4, 0]],
        },
        "fbg": {"type": "LineString", "coordinates": [[0, 1], [1, 0], [2, 1]]},
    }
    topo = Join(data).to_dict()

    assert topo["junctions"] == []


# when a line ABCA is closed, there is no junction at A
def test_join_line_ABCA_is_closed():
    data = {
        "abca": {"type": "LineString", "coordinates": [[0, 0], [1, 0], [0, 1], [0, 0]]}
    }
    topo = Join(data).to_dict()
    assert topo["junctions"] == []


# when a ring ABCA is closed, there are no junctions
def test_join_ring_ABCA_is_closed():
    data = {
        "abca": {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [0, 1], [0, 0]]]}
    }
    topo = Join(data).to_dict()

    assert topo["junctions"] == []


# exact duplicate rings ABCA & ABCA share the arc ABCA, but contain no junctions
def test_join_exact_duplicate_rings_ABCA_ABCA_share_ABCA():
    data = {
        "abca": {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [0, 1], [0, 0]]]},
        "abca2": {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [0, 1], [0, 0]]]},
    }
    topo = Join(data).to_dict()

    assert topo["junctions"] == []


# reversed duplicate rings ABCA & ACBA share the arc ABCA, but contain no juctions
def test_join_exact_duplicate_rings_ABCA_ACBA_share_ABCA():
    data = {
        "abca": {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [0, 1], [0, 0]]]},
        "acba": {"type": "Polygon", "coordinates": [[[0, 0], [0, 1], [1, 0], [0, 0]]]},
    }
    topo = Join(data).to_dict()

    assert topo["junctions"] == []


# coincident rings ABCA & BCAB share the arc BCAB, but contain no junctinos
# this is a problem though as they are considered equal in a MultiPolygon geometry.
# test will pass, but coincident rings should be rotated before dedup
def test_join_coincident_rings_ABCA_BCAB_share_BCAB():
    data = {
        "abca": {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [0, 1], [0, 0]]]},
        "bcab": {"type": "Polygon", "coordinates": [[[1, 0], [0, 1], [0, 0], [1, 0]]]},
    }
    topo = Join(data).to_dict()

    assert topo["junctions"] == []


# coincident rings ABCA & BACB share the arc BCAB, but contain no junctions
def test_join_coincident_rings_ABCA_BACB_share_BCAB():
    data = {
        "abca": {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [0, 1], [0, 0]]]},
        "bacb": {"type": "Polygon", "coordinates": [[[1, 0], [0, 0], [0, 1], [1, 0]]]},
    }
    topo = Join(data).to_dict()

    assert topo["junctions"] == []


# coincident rings ABCA & DBED share the point B, but is no junction
def test_join_coincident_rings_ABCA_DBED_share_B():
    data = {
        "abca": {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [0, 1], [0, 0]]]},
        "dbed": {"type": "Polygon", "coordinates": [[[2, 1], [1, 0], [2, 2], [2, 1]]]},
    }
    topo = Join(data).to_dict()

    assert topo["junctions"] == []


# coincident ring ABCA & line DBE share the point B
def test_join_coincident_ring_ABCA_and_line_DBE_share_B():
    data = {
        "abca": {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [0, 1], [0, 0]]]},
        "dbe": {"type": "LineString", "coordinates": [[2, 1], [1, 0], [2, 2]]},
    }
    topo = Join(data).to_dict()

    assert topo["junctions"] == []


# should keep junctions from partly shared paths
# this test was added since the a shared path of ABC and another shared path of ABD
# only kept the junctions at A, C and D, but not at B.
def test_join_shared_junctions_in_shared_paths():
    data = geopandas.read_file(geopandas.datasets.get_path("naturalearth_lowres"))
    data = data[
        (data.name == "Togo") | (data.name == "Benin") | (data.name == "Burkina Faso")
    ]
    topo = Join(data).to_dict()

    assert len(topo["junctions"]) == 6


# this test was added since a shared path can be detected of two linestrings where
# the shared path is partly from the start and partly of the end part of the
# linestring. If any shared path are detected also add the first coordinates of both
# linestrings to be considerd as junction. Not sure what happened if this introduces
# another problem since this coordinates may not be unique anymore, and this can be
# skipped as a junction..
def test_join_shared_segment_partly_start_partly_end_segment():
    data = geopandas.read_file(geopandas.datasets.get_path("naturalearth_lowres"))
    data = data[
        (data.name == "Eritrea") | (data.name == "Ethiopia") | (data.name == "Sudan")
    ]
    topo = Join(data).to_dict()

    assert len(topo["junctions"]) == 6


def test_join_non_noded_interesection():
    data = geopandas.read_file(geopandas.datasets.get_path("naturalearth_lowres"))
    topo = Join(data).to_dict()  # , quant_factor=1e6)

    assert len(topo["junctions"]) == 321


def test_join_super_function_extract():
    data = geometry.GeometryCollection(
        [
            geometry.Polygon([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]),
            geometry.Polygon([[1, 0], [2, 0], [2, 1], [1, 1], [1, 0]]),
        ]
    )
    topo = Join(data).to_dict()

    assert len(list(topo.keys())) == 9


def test_join_point():
    data = [{"type": "Point", "coordinates": [0.5, 0.5]}]
    topo = Join(data).to_dict()

    assert topo["bbox"] == (0.5, 0.5, 0.5, 0.5)


def test_join_prequantize_points():
    data = [
        {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]},
        {"type": "Point", "coordinates": [-0.5, 1.5]},
    ]
    topo = Join(data, options={"prequantize": True}).to_dict()

    assert topo["bbox"] == (-0.5, 0.0, 1.0, 1.5)


def test_join_linemerge_multilinestring():
    data = [
        {"type": "LineString", "coordinates": [(0, 0), (10, 0), (10, 5), (20, 5)]},
        {
            "type": "LineString",
            "coordinates": [
                (5, 0),
                (25, 0),
                (25, 5),
                (16, 5),
                (16, 10),
                (14, 10),
                (14, 5),
                (0, 5),
            ],
        },
    ]
    topo = Join(data).to_dict()

    assert len(topo["linestrings"]) == 2
    assert len(topo["junctions"]) == 7

    # test the shared_paths_approach using dicts
    def test_join_shared_paths_dict():
        data = {
            "cba": {"type": "LineString", "coordinates": [[2, 0], [1, 0], [0, 0]]},
            "ab": {"type": "LineString", "coordinates": [[0, 0], [1, 0]]},
        }
        topo = Join(data, options={"shared_paths": "dict"}).to_dict()

        assert geometry.MultiPoint(topo["junctions"]).equals(
            geometry.MultiPoint([(0.0, 0.0), (1.0, 0.0)])
        )

    # test a list of two invalid geometric objects with prequantize True
    def test_join_invalid_prequantize():
        data = [
            {
                "type": "MultiPolygon",
                "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
            },
            {
                "type": "MultiPolygon",
                "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
            },
        ]
        topo = Join(data, options={"prequantize": True}).to_dict()

        assert len(topo["junctions"]) == 0
