import numpy as np
from lsst.sims.utils import haversine, _hpid2RaDec
import lsst.sims.sky_brightness_pre as sb
import healpy as hp

sec2days = 1./(3600.*24.)


class Speed_observatory(object):
    """
    A very very simple observatory model that will take observation requests and supply
    current conditions.
    """
    def __init__(self, mjd_start=0., ang_speed=5.,
                 readtime=2., settle=2., filtername=None, f_change_time=120.,
                 nside=32):
        """
        
        """
        self.mjd = mjd_start
        self.ang_speed = np.radians(ang_speed)
        self.settle = settle
        self.f_change_time = f_change_time

        # Load up the sky brightness model
        self.sky = sb.SkyBrightnessPre()

        # Start out parked
        self.ra = None
        self.dec = None
        self.filtername = None

        # Set up all sky coordinates
        hpids = np.arange(hp.nisde2npix(nside))
        self.ra_all_sky, self.dec_all_sky = _hpid2RaDec(nside, hpids)

    def slew_time(self, ra, dec):
        """
        Compute slew time to new ra, dec position
        """
        dist = haversine(ra, dec, self.ra, self.dec)
        time = dist / self.ang_speed
        return time

    def return_status(self):
        """
        Return a dict full of the current info about the observatory and sky.
        """
        result = {}
        result['mjd'] = self.mjd
        result['sky'] = self.sky.returnMags(self.ra_all_sky, self.dec_all_sky, self.mjd)
        result['m5_percentile']
        return result


    def check_mjd(self, mjd):
        """
        If an mjd is not in daytime or downtime
        """
        return True, mjd

    def attempt_observe(self, observation):
        """
        Check an observation, if there is enough time, execute it and return it, otherwise, return none.
        """
        
        # If we were in a parked position, assume no time lost to slew, settle, filter change
        if self.ra is not None:
            st = self.slew_time(observation['ra'], observation['dec'],
                                self.ra, self.dec)
            self.filtername = observation['filter']
            settle = self.settle
            if self.filtername != observation['filter']:
                ft = self.f_change_time
            else:
                ft = 0.
        else:
            st = 0.
            settle = 0.
            ft = 0.
        
        rt = (observation['nexp']-1.)*self.readtime
        total_time = st + rt + observation['exptime'] + settle
        
        check_result, jump_mjd = self.check_mjd(self.mjd + total_time)
        if check_result:
            # time the shutter should open
            observation['mjd'] = self.mjd + (st + ft + self.settle) * sec2days
            self.mjd += total_time*sec2days
            self.ra = observation['ra']
            self.dec = observation['dec']
            self.filtername = observation['filter']
            return observation
        else:
            self.mjd = jump_mjd
            self.ra = None
            self.dec = None
            return None
