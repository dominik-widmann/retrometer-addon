#!/usr/bin/env python
import time
import logging
from src.tick_detector import ScalarPeriodCounter


class RetroMeter:
    def __init__(self, magnetometer, mag_axis, max_period_length, min_amplitude, max_amplitude, min_std, is_verbose=False):
        """Create a retro meter object.

        Args:
            magnetometer (Magnetometer): _description_
            mag_axis (String): One of "x", "y", "z". Selects which magnetometer axis to use for counting.
            expected_axis_min (float): _description_
            expected_axis_max (float): _description_
        """
        self._magnetometer = magnetometer

        # initialize the period counter with expected magx min and max values
        self._period_counter = ScalarPeriodCounter( max_period_length, min_amplitude, max_amplitude, min_std)
        self._mag_axis = mag_axis

        # configure printing
        self._is_verbose = is_verbose

    def is_count_updated(self):
        """
        Returns true if the measured tick count could have changed since the last update_and_get_meter_ticks() call. This does not mean that the count value has actually changed.
        """
        return self._magnetometer.is_new_meas_available()

    def update_and_get_meter_ticks(self):
        """
        Update and get the current number of meter ticks. Should only be called when is_count_updated() returns true. 
        """
        (x,y,z) = self._magnetometer.read_magnetometer()
        mag_dict = {"x": x, "y": y, "z" : z}
        self._period_counter.record_scalar(mag_dict[self._mag_axis])
        count = self._period_counter.get_count()

        if self._is_verbose:
            print("Count: {}, x: {:10.3f}, y: {:10.3f}, z: {:10.3f}".format(count, x,y,z))
        return count



