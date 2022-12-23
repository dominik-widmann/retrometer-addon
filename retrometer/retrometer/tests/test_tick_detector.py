import unittest
from unittest.mock import MagicMock
from src.tick_detector import ScalarPeriodCounter
import numpy as np


class TestScalarPeriodCounter(unittest.TestCase):
    def setUp(self) -> None:
        sample_time = 0.05
        max_period_time = 5.0  # seconds
        max_period_length = int(max_period_time/sample_time)
        min_amplitude = 20
        max_amplitude = 8000
        min_std = 20

        # Setup counter
        self.counter = ScalarPeriodCounter(
            max_period_length, min_amplitude, max_amplitude, min_std)

        return super().setUp()

    def helper_generate_sine(self, amplitude, period, end_time, sample_time):
        """Creates a vector y = a*sin(2*pi/period*time_vec)

        Args:
            amplitude (_type_): _description_
            period (_type_): _description_
            time_vec (_type_): _description_
        """
        time_vec = np.linspace(0, end_time, int(end_time/sample_time)+1)
        return time_vec, np.multiply(amplitude, np.sin(np.multiply(2.0*np.pi/period, time_vec)))

    def test_sine(self):
        # Given a scalar period counter configured with the above parameters

        # When it gets excited with a sine wave like this
        times, values = self.helper_generate_sine(
            amplitude=300, period=5.0, end_time=60.0, sample_time=0.05)

        counts = []
        for value in values:
            self.counter.record_scalar(value)
            counts.append(self.counter.get_count())

        # We expect a count of 2 because it only starts counting when its buffer is full and that has been configured to 10 times the max period
        self.assertEqual(self.counter.get_count(), 2)

    def test_sines_with_noise_and_outliers(self):
        # Given a scalar period counter configured with the above parameters

        # When it gets excited with a sine, then nothing+a bit of noise and then a sine again
        times0, values0 = self.helper_generate_sine(
            amplitude=5, period=.2, end_time=200.0, sample_time=0.05)
        times1, values1 = self.helper_generate_sine(
            amplitude=300, period=5.0, end_time=60.0, sample_time=0.05)
        times1 = times1 + times0[-1]+0.05
        pause_time = 5.0*100.0  # more than one buffer length
        times2, values2 = self.helper_generate_sine(
            amplitude=5, period=.2, end_time=200.0, sample_time=0.05)
        times2 = times2 + times1[-1]+0.05
        values3 = values1
        times3 = times1 + times2[-1] + 0.05
        times4, values4 = self.helper_generate_sine(
            amplitude=290, period=15.0, end_time=150.0, sample_time=0.05)
        times4 = times4 + times3[-1] + 0.05

        times = np.concatenate([times0, times1, times2, times3, times4])
        values = np.concatenate([values0, values1, values2, values3, values4])

        # Add some crazy outliers to make sure the calibrator handles them correctly
        outlier_factors = np.ones(values.shape)*1.0
        for index in [1, 87, 130, 202, 543, 2345, 4352]:
            outlier_factors[index] = 100.0
        values = np.multiply(values, outlier_factors)

        # Add a bit of noise
        values = np.random.normal(values, 10.0)

        counts = []
        calib_min = []
        calib_max = []
        calib_std = []
        for value in values:
            self.counter.record_scalar(value)
            counts.append(self.counter.get_count())
            calib_min.append(self.counter._calibrator._current_min)
            calib_max.append(self.counter._calibrator._current_max)
            calib_std.append(self.counter._calibrator._current_std)

        # import matplotlib.pyplot as plt
        # plt.subplot(2,1,1)
        # plt.plot(times, values)
        # plt.plot(times,calib_min)
        # plt.plot(times,calib_max)
        # plt.plot(times, calib_std)
        # plt.subplot(2,1,2)
        # plt.plot(times,counts)
        # plt.show()

        # We expect a count of 12 + 12 + 10 = 34
        self.assertEqual(self.counter.get_count(), 34)

    def test_calibration_confirmation_considered(self):
        # Given a scalar period counter with a magic mock as a calibrator that returns that calibration is not yet confirmed
        self.counter._calibrator = MagicMock()
        self.counter._calibrator.get_calibration_progress_percentage.return_value = 99
        self.counter._calibrator.get_expected_min_max.return_value = (10, 90)

        # When we record a value to the period counter
        self.counter.record_scalar(100.0)

        # We expect that the min and max estimates are considered
        self.counter._calibrator.get_calibration_progress_percentage.assert_called()

        # When calibration confirmation is finished
        # use a fresh mock to track the following function calls
        self.counter._calibrator = MagicMock()
        self.counter._calibrator.get_calibration_progress_percentage.return_value = 100

        # When a value is recorded
        self.counter.record_scalar(90.0)

        # We expect that the min and max estimates where no longer considered
        self.counter._calibrator.get_expected_min_max.return_value.assert_not_called()


if __name__ == '__main__':
    unittest.main()
