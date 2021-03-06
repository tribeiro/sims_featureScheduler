import numpy as np
import lsst.sims.featureScheduler as fs
from lsst.sims.speedObservatory import Speed_observatory
import healpy as hp


if __name__ == "__main__":

    survey_length = 365.25  # days
    # Define what we want the final visit ratio map to look like
    target_map = fs.standard_goals()['r']
    filtername = 'r'

    bfs = []
    bfs.append(fs.M5_diff_basis_function(filtername=filtername, teff=False))
    bfs.append(fs.Target_map_basis_function(target_map=target_map, filtername=filtername,
                                            out_of_bounds_val=hp.UNSEEN))
    bfs.append(fs.Quadrant_basis_function(quadrants='S', azWidth=15., maxAlt=75.))
    bfs.append(fs.Slewtime_basis_function(filtername=filtername))

    weights = np.array([1., 0.2, 1., 4.])
    survey = fs.Greedy_survey_fields(bfs, weights, block_size=1, filtername=filtername)
    scheduler = fs.Core_scheduler([survey])

    observatory = Speed_observatory()
    observatory, scheduler, observations = fs.sim_runner(observatory, scheduler,
                                                         survey_length=survey_length,
                                                         filename='one_filter_south.db',
                                                         delete_past=True)
