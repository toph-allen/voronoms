import pandas as pd
import numpy as np
from scipy.spatial import Voronoi
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
from tqdm import tqdm #TODO: make this conditional on verbose option


def make_admin_polygons(country, admin_level, geonames, shapes, clean=None):
    admin_geonames = get_admin_geonames(country, admin_level, geonames)
    voronoi_geonames = get_voronoi_geonames(country, admin_level, geonames)

    # Get the outline for the country we're handling
    shapes["country_code"] = geonames.loc[shapes.index, "country_code"]
    country_outline = shapes.query("country_code == '{}'".format(country)).iloc[0][
        "geometry"
    ]

    # Draw the Voronoi diagram
    print("Creating Voronoi diagram...")
    country_voronoi = Voronoi([x.coords[0] for x in voronoi_geonames.points])

    # Polygon-generating loop
    admin_polygons = []
    print("Generating polygons...")
    for geonameid, admin_geoname in tqdm(admin_geonames.iterrows(), total=len(admin_geonames)):
        admin_polygons.append(
            extract_polygon_from_voronoi(
                admin_geoname, geonames, voronoi_geonames, country_voronoi, country_outline
            )
        )

    if clean is None or clean == "none":
        pass
    elif clean == "cutoff":
        print("Cleaning polygons...")
        admin_polygons = clean_polygons_max_diff_cutoff(admin_polygons)
    elif clean == "simple":
        print("Cleaning polygons...")
        admin_polygons = clean_polygons_simple(admin_polygons)

    return admin_polygons


def admin_cols(admin_level=None):
    return ["admin{}_code".format(i) for i in range(1, admin_level + 1)]


def get_admin_geonames(country, admin_level, geonames):
    """
    This function returns the GeoNames from a specified admin level in a country.
    """

    # Get the admin geonames we'll be finding polygons for.
    admin_predicate = "country_code == '{}' & feature_class == 'A' & feature_code == 'ADM{}'".format(
        country, admin_level
    )

    admin_geonameids = (
        geonames.query(admin_predicate).loc[:, admin_cols(admin_level)].drop_duplicates().dropna()
    ).index
    admin_geonames = geonames.loc[admin_geonameids]
    return admin_geonames


def get_voronoi_geonames(country, admin_level, geonames):
    """
    This function returns all GeoNames which have an admin code at the specified level, and
    thus can be used to make inferences about the admin area shapes.
    """
    # TODO: This is super inefficient.
    admin_geonames = get_admin_geonames(country, admin_level, geonames)
    voronoi_predicate_parts = ["country_code == '{}'".format(country)]
    for col in admin_cols(admin_level):
        voronoi_predicate_parts.append("{} in @admin_geonames.{}".format(col, col))
    voronoi_predicate = " & ".join(voronoi_predicate_parts)

    voronoi_geonames = geonames.query(voronoi_predicate)
    return voronoi_geonames


def extract_polygon_from_voronoi(admin_geoname, geonames, voronoi_geonames, country_voronoi, country_outline):
    # Get the indices of the voronoi regions in this admin area
    admin_col_names = [col for col in admin_geoname.index if "admin" in col]
    polygon_predicate_parts = ["country_code == '{}'".format(admin_geoname.country_code)]
    for col in admin_col_names:
        if not pd.isnull(admin_geoname[col]):
            polygon_predicate_parts.append("{} == '{}'".format(col, admin_geoname[col]))
    polygon_predicate = " & ".join(polygon_predicate_parts)
    polygon_geonames = geonames.query(polygon_predicate)
    polygon_geonameids = polygon_geonames.index

    # Figure out which Voronoi regions we need.
    # The Voronoi module calls them "regions" but I'm calling them
    # "cells" for clarity's sake.
    point_indices = np.where(voronoi_geonames.index.isin(polygon_geonameids))[0]
    cell_indices = country_voronoi.point_region[point_indices]

    # Get the points for the regions and make them into Polygons
    admin_cells = []
    for cell_idx in cell_indices:
        vert_indices = country_voronoi.regions[cell_idx]
        if -1 in vert_indices:
            continue
        cell = Polygon(
            [country_voronoi.vertices[vert_idx] for vert_idx in vert_indices]
        )
        admin_cells.append(cell)
    # The unary union is the slow part.
    unified_cells = unary_union(MultiPolygon(admin_cells)).intersection(country_outline)
    if type(unified_cells) is Polygon:
        unified_cells = MultiPolygon([unified_cells])
    return unified_cells


# Cleaning functions

def clean_polygons_simple(admin_polygons):
    """
    Deletes any part of an admin polygon that is entirely
    contained within another admin area in the country.
    """
    # Fill in holes in the polygons
    filled_admin_polygons = []
    for admin_polygon in admin_polygons:
        filled_poly = [
            Polygon(poly.exterior) for poly in admin_polygon
        ]
        filled_admin_polygons.append(MultiPolygon(filled_poly))

    # Remove any polygons that are contained inside the now-filled polygons
    cleaned_admin_polygons = []
    for this_area in tqdm(filled_admin_polygons):
        # Make a flat list of subpolygons of other admin regions
        other_polys = []
        for other_area in (filled_admin_polygons):
            if other_area is not this_area:
                for poly in other_area:
                    other_polys.append(poly)

        not_within_others = []
        for poly in this_area:
            if not any([poly.within(other_poly) for other_poly in other_polys]):
                not_within_others.append(poly)
        new_area = MultiPolygon(not_within_others)
        cleaned_admin_polygons.append(new_area)
    return cleaned_admin_polygons


def clean_polygons_max_diff_cutoff(admin_polygons):
    """
    Separates polygons in each admin area into "must keep" and "can delete" bins based on the largest cutoff of differences between sizes. "Can delete" polygons will be deleted if they are contained by another admin area. "Must keep" polygons will be kept, and will cut out holes in admin areas that contain them.

    This should work better for single-area admin areas which are entirely contained in other regions.

    It will likely fail for admin areas with no clear cutoff, or with multiple groups of sizes. More complex heuristics, such as k-means clustering, or an analysis of the entire group of admin areas to determine the best route, are probably a good aim for the next version.
    """
    # Fill in holes in the polygons
    filled_polygons = []
    for admin_polygon in admin_polygons:
        filled_poly = [
            Polygon(poly.exterior) for poly in admin_polygon
        ]
        filled_polygons.append(MultiPolygon(filled_poly))

    # Separate polygons per region into "must keep" and "can delete". 
    separated_polygons = [separate_deletion_candidates(p) for p in filled_polygons]
    must_keep = [x[0] for x in separated_polygons]
    can_delete = [x[1] for x in separated_polygons]

    # First we'll iterate through the polygons we HAVE to keep. We'll compare
    # each one to each other polygon we have to keep. If it contains another
    # must-keep polygon, we'll cut that out from it. Then we'll add the
    # resulting shape to our new list.
    cleaned_polygons = []
    for this_area in tqdm(must_keep):
        other_polys = []
        for other_area in must_keep:
            if other_area is not this_area:
                for poly in other_area:
                    other_polys.append(poly)
        new_area = []
        for a in this_area:
            for b in other_polys:
                if a.contains(b):
                    a = a.difference(b)
            new_area.append(a)
        cleaned_polygons.append(new_area)

    # Next we'll operate on the polys which we can delete if they're contained.
    # This will operate in two stages.

    # first, deleting any which are contained in a must-keep area.
    first_pass_kept = []
    for this_area in tqdm(can_delete):
        # We'll only draw polygons from the must_keep areas at first.
        keep_polys = []
        for other_area in cleaned_polygons:
            for poly in other_area:
                keep_polys.append(poly)
        not_contained = []
        for poly in this_area:
            if not any([poly.within(other_poly) for other_poly in other_polys]):
                not_contained.append(poly)
        first_pass_kept.append(not_contained)

    # Second, deleting any which are contained in another candidate area.
    for i, this_area in tqdm(enumerate(first_pass_kept), total = len(first_pass_kept)):
        other_polys = [] # We'll only draw polygons from the must_keep areas at first.
        for other_area in first_pass_kept:
            if other_area is not this_area:
                for poly in other_area:
                    other_polys.append(poly)
        not_contained = []
        for poly in this_area:
            if not any([poly.within(other_poly) for other_poly in other_polys]):
                not_contained.append(poly)
        cleaned_polygons[i].extend(not_contained)

    new_admin_areas = [MultiPolygon(area) for area in cleaned_polygons] 
    return new_admin_areas


def create_delete_eligibility_mask(polys):
    if len(polys) == 1:
        return [False]
    areas = [poly.area for poly in polys]
    sorted_areas = np.sort(areas)
    area_diffs = np.diff(sorted_areas)
    max_diff = np.argmax(area_diffs)
    max_delete = sorted_areas[max_diff]
    return np.less_equal(areas, max_delete)


def separate_deletion_candidates(admin_polygon):
    if len(admin_polygon) == 0:
        return ([], [])
    admin_polygon = np.array(admin_polygon)
    mask = create_delete_eligibility_mask(admin_polygon)
    must_keep = admin_polygon[np.invert(mask)]
    can_delete = admin_polygon[mask]
    return must_keep, can_delete