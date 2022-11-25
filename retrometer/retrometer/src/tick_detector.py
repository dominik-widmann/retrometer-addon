import collections
import numpy as np

class HysteresisTrigger:
    def __init__(self, activation_threshold_ratio, deactivation_threshold_ratio):
        assert activation_threshold_ratio > deactivation_threshold_ratio
        self.activation_threshold_ratio = activation_threshold_ratio
        self.deactivation_threshold_ratio = deactivation_threshold_ratio
        self.activation_threshold = 0.0
        self.deactivation_threshold = 0.0
        self._is_activated = False
        self._is_configured = False
        

    def configure_min_max(self,min,max):
        self.activation_threshold = min + self.activation_threshold_ratio*(max-min)
        self.deactivation_threshold = min + self.deactivation_threshold_ratio*(max-min)
        self._is_configured = True

    def input(self, value):
        """
        Processes input values and sets the activation state based on the configured hysteresis behavior
        """
        is_triggered = False

        if not self._is_configured:
            # return that we are not triggered
            return False

        # Check if we are switching to activated to return that as a trigger
        if not self._is_activated:
            is_triggered = value >= self.activation_threshold
            self._is_activated = is_triggered
        else:
            # if value is still above deactivation threshold we keep activated
            self._is_activated = value > self.deactivation_threshold

        return is_triggered
        


class MinMaxCalibrator:
    def __init__(self, max_buffer_length, min_amplitude, max_amplitude, min_std):
        """Create a min max calibrator that monitors an oscillation and determins min and max values.

        Args:
            max_buffer_length (_type_): _description_
        """
        self._value_window = collections.deque(maxlen=max_buffer_length)
        self._current_min = np.inf
        self._current_max = -np.inf
        self._current_std = 0
        self._min_amplitude = min_amplitude
        self._max_amplitude = max_amplitude
        self._min_std = min_std
        self._is_calibrated = False

    def input(self, value):
        """provide an input value for calibration. Should be called regularly. Triggers all sorts of calculations

        Args:
            value (_type_): _description_
        """
        # add value to the buffer
        self._value_window.append(value)
        # check if a signification amount of excitation has been observed
        if self._is_sufficiently_excited():
            # If yes, update the min and max values with 5 and 95 percentiles to be robust against outliers
            self._current_min = min(self._current_min, np.percentile(self._value_window,5))
            self._current_max = max(self._current_max, np.percentile(self._value_window,95))
            # Set the calibrated flag
            self._is_calibrated = True

    def is_calibrated(self):
        return self._is_calibrated

    def get_expected_min_max(self):
        return (self._current_min, self._current_max)

    def _is_sufficiently_excited(self):

        # Condition 1: buffer full
        is_buffer_full = len(self._value_window) == self._value_window.maxlen

        # Condition 2: min and max amplitude between 5% and 95% value are satisfied
        biggest_amplitude = abs(np.percentile(self._value_window,95) - np.percentile(self._value_window,5))/2.0
        is_amplitude_range_ok =  biggest_amplitude > self._min_amplitude and biggest_amplitude < self._max_amplitude

        # Condition 3: high enough standard deviation
        self._current_std = np.std(self._value_window)
        is_variance_big_enough = self._current_std > self._min_std

        return is_buffer_full and is_amplitude_range_ok and is_variance_big_enough




class ScalarPeriodCounter:
    def __init__(self, max_period_length, min_amplitude, max_amplitude, min_std):
        hysteresis_activation_threshold_ratio = 0.8 # activation if 80 percent of expected amplitude is reached
        hysteresis_deactivation_threshold_ratio = 0.7 # deactivation at 70 percent

        # Initialize trigger
        self._trigger = HysteresisTrigger(hysteresis_activation_threshold_ratio, hysteresis_deactivation_threshold_ratio)

        # Initialize period counter
        self._counter = 0

        # Initialize min max calibrator
        self._calibrator = MinMaxCalibrator(10*max_period_length, min_amplitude, max_amplitude, min_std)

    def record_scalar(self, scalar):
        # input scalar to the calibrator
        self._calibrator.input(scalar)

        # Check if calibrator is calibrated and update the trigger with the min max estimates
        if self._calibrator.is_calibrated():
            # If yes, get the min max value estimates and configure the hysteresisTrigger with them
            min, max = self._calibrator.get_expected_min_max()
            self._trigger.configure_min_max(min, max)

        if self._trigger.input(scalar):
            # a new period has started, increment period counter
            self._counter = self._counter + 1

    def get_count(self):
        return self._counter


