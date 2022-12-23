import unittest
from src.tick_detector import MinMaxCalibrator
import numpy as np
import time


class TestMinMaxCalibrator(unittest.TestCase):
    def setUp(self) -> None:
        sample_time = 0.05
        max_period_time = 5.0  # seconds
        max_period_length = int(max_period_time/sample_time)
        min_amplitude = 20
        max_amplitude = 8000
        min_std = 20

        # Setup calibrator
        self.calibrator = MinMaxCalibrator(
            10, min_amplitude, max_amplitude, min_std, calibration_confirm_duration=10.0)

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

    def test_sine_min_max(self):
        # Given min max calibrator configured with the above parameters

        # When it gets excited with a sine wave like this
        times, values = self.helper_generate_sine(
            amplitude=300, period=5.0, end_time=60.0, sample_time=0.05)

        # We expect progress to be 0% before excitation starts
        self.assertEqual(
            self.calibrator.get_calibration_progress_percentage(), 0)

        for value in values:
            self.calibrator.input(value)

        # We expect progress at 1% just after sufficient excitation was available
        self.assertEqual(
            self.calibrator.get_calibration_progress_percentage(), 1)

        # We expect the min max values to be correctly estimated
        estimated_min_value = np.percentile(values, 5)
        estimated_max_value = np.percentile(values, 95)
        self.assertAlmostEqual(self.calibrator.get_expected_min_max()[0],
                               estimated_min_value, delta=2)
        self.assertAlmostEqual(self.calibrator.get_expected_min_max()[1],
                               estimated_max_value, delta=2)

        # We expect around 50 percent progress after 5 seconds since we configured 10s calibration confirmation time
        time.sleep(5)
        self.assertAlmostEqual(
            self.calibrator.get_calibration_progress_percentage(), 50, delta=5)

        # We expect 100% progress after 11s, which is 1s beyond calibration confirmation time
        time.sleep(6)
        self.assertEqual(
            self.calibrator.get_calibration_progress_percentage(), 100)


if __name__ == '__main__':
    unittest.main()
