import numpy as np
import healpy as hp
import matplotlib.pylab as plt
import lsst.sims.featureScheduler as fs
from lsst.sims.featureScheduler.observatory import Speed_observatory


if __name__ == "__main__":

    survey_length = 1  # days
    # Define what we want the final visit ratio map to look like
    target_maps = fs.standard_goals()

    filters = ['u', 'g', 'r', 'i', 'z', 'y']
    surveys = []
    pairs_in = 'gri'
    for filtername in filters:
        bfs = []
        bfs.append(fs.Depth_percentile_basis_function(filtername=filtername))
        bfs.append(fs.Target_map_basis_function(target_map=target_maps[filtername], filtername=filtername))
        bfs.append(fs.Filter_change_basis_function(filtername=filtername))
        if filtername in pairs_in:
            bfs.append(fs.Visit_repeat_basis_function(filtername='gri'))
            weight = [1., 1., 0.2, 1.]
        else:
            weight = [1., 1., 0.2]
        surveys.append(fs.Simple_greedy_survey_fields(bfs, weight, filtername=filtername))

    scheduler = fs.Core_scheduler(surveys)

    observatory = Speed_observatory(quickTest=False)
    observatory, scheduler, observations = fs.sim_runner(observatory, scheduler, survey_length=survey_length,
                                                         filename='six_w.db')
    
# 30 days took 27minutes. So 10 years would be 54 hours. So really would be nice to multiprocess some things.