import pandas as pd
import numpy as np
import geopandas as gpd
from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt
import shapely

def generate_voronoms(country, admin_level, geonames, shapes):
    admin_cols = ["admin{}_code".format(i) for i in range(1, admin_level + 1)]

    # Get the admin geonames we'll be finding polygons for.
    admin_predicate = "country_code == '{}' & feature_class == 'A'".format(country)
    admin_geonameids = (
        geonames.query(admin_predicate).loc[:, admin_cols].
        drop_duplicates().dropna()
    ).index
    admin_geonames = geonames.loc[admin_geonameids]

    # Get the geonames we'll use for the Voronoi diagram.
    # We only draw the Voronoi diagram with GeoNames which directly
    # have our admin level of interest listed in their admin2_code column.
    # This is because:
    # 1. GeoNames have multiple levels of hierarchy assigned, but we can't be sure that they are coherent between levels.
    # 2. So we have to draw the Voronoi diagram at one level of hierarchy.
    # 3. Drawing the Voronoi diagram is fairly costly, so we want to do it once, so;
    # 4. We want to get all geonames with *this* level of admin hierarchy in *this* country to draw our voronoi diagram.
    voronoi_predicate_parts = ["country_code == '{}'".format(country)]
    for col in admin_cols:
        voronoi_predicate_parts.append("{} in @admin_geonames.{}".format(col, col))
    voronoi_predicate = " & ".join(voronoi_predicate_parts)

    voronoi_geonames = geonames.query(voronoi_predicate)

    # Get the outline for the country we're handling
    shapes["country_code"] = geonames.loc[shapes.index, "country_code"]
    country_outline = shapes.query("country_code == '{}'".format(country)).iloc[0]["geometry"]

    # Draw the Voronoi diagram
    print("Creating Voronoi diagram...")
    country_voronoi = Voronoi([x.coords[0] for x in voronoi_geonames.points])
    print("Done.")

    admin_polygons = []
    for geonameid, admin_geoname in tqdm(admin_geonames.iterrows(), total = len(admin_geonames)):
        # Get the indices of the voronoi regions in this admin area
        polygon_predicate_parts = ["country_code == '{}'".format(country)]
        for col in admin_cols:
            polygon_predicate_parts.append("{} == @admin_geoname.{}".format(col, col))
        polygon_predicate = " & ".join(polygon_predicate_parts)
        polygon_geonames = geonames.query(polygon_predicate)
        polygon_geonameids = polygon_geonames.index

        # Figure out which Voronoi regions we need.
        # The Voronoi module calls them "regions" but I'm calling them
        # "cells" for clarity's sake.
        point_indices = np.where(voronoi_geonames.index.isin(polygon_geonameids))[0]
        cell_indices = country_voronoi.point_region[point_indices]

        # Get the points for the regions and make them into Polygons
        admin_voronoi_cells = []
        for i in cell_indices:
            cell = shapely.geometry.Polygon(
                [country_voronoi.vertices[vert_idx]
                 for vert_idx in country_voronoi.regions[i]]
            )
            admin_voronoi_cells.append(cell)
        """
        We take the MultiPolygon made from the Voronoi cells in an admin region
        and run the following operations:
            1. Removes any Voronoi cells with no neighbors. This should be improved.
            2. Uses Shapely's unary union function to join all the polygons.
            3. Intersects the resulting shape with the country's outlines.
        """
        non_singleton_cells = []
        for cell in admin_voronoi_cells:
                # Because we don't need to _count_ the number of adjacent regions,
                # we iterate through until we find an adjacent region, and as soon as we
                # find a neighbor we add it to the list of regions to include.
            any_neighbors = False
            for other_cell in admin_voronoi_cells:
                if cell.touches(other_cell):
                    any_neighbors = True
                    break
            if any_neighbors == True:
                non_singleton_cells.append(cell)

        admin_multipolygon = shapely.geometry.MultiPolygon(non_singleton_cells)
        admin_polygon = shapely.ops.unary_union(admin_multipolygon).intersection(country_outline)
        # The following line should actually come after the unary union but before the intersection.
        # polygon = polygon.simplify(tolerance = 0.02).buffer(0)
        admin_polygons.append(admin_polygon)
    return admin_polygons