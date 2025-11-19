import pandas as pd
import numpy as np
from scipy import stats
import math
from typing import Union, List, Tuple
from dataclasses import dataclass

@dataclass
class SampleSizeResult:
    """Class to store sample size calculation results for A/B testing experiments.
    
    Attributes:
        metric_name (str): Name of the metric being tested
        mde (float): Minimum Detectable Effect (MDE) used in the calculation
        control_sample_size (int): Required sample size for the control group
        treatment_sample_size (int): Required sample size for the treatment group
        total_sample_size (int): Total required sample size across all groups
        experiment_days (int, optional): Estimated number of days needed to run the experiment
    """
    metric_name: str
    mde: float
    control_sample_size: int
    treatment_sample_size: int
    total_sample_size: int
    experiment_days: int = None

class SampleSizeCalculator:
    """
    A comprehensive calculator for determining sample sizes in A/B testing experiments.
    Supports three types of metrics: mean, proportion, and ratio metrics.
    
    This calculator helps determine the minimum sample size required to detect
    a specified effect size with a given statistical power and significance level.
    """
    
    def __init__(self, significance_level: float = 0.05, power: float = 0.8):
        """
        Initialize the calculator with statistical parameters.
        
        Args:
            significance_level (float): The Type I error rate (alpha) for the test. Default is 0.05.
            power (float): The desired statistical power (1 - beta). Default is 0.8.
        """
        self.significance_level = significance_level
        self.power = power
        self.z_beta = stats.norm.ppf(power)
        
    def _get_critical_value(self, is_two_sided: bool = True) -> float:
        """
        Calculate the critical Z-value for the given significance level.
        
        Args:
            is_two_sided (bool): Whether to use two-sided test. Default is True.
            
        Returns:
            float: The critical Z-value for the specified significance level
        """
        if is_two_sided:
            return stats.norm.ppf(1 - self.significance_level / 2)
        return stats.norm.ppf(1 - self.significance_level)
    
    def calculate_binary_metric_sample_size(self, baseline_rate: float, mde: float, k: float = 1, is_two_sided: bool = True) -> int:
        """
        Calculate required sample size for binary metrics (e.g., conversion rates).
        
        This method is suitable for metrics that follow a binomial distribution,
        such as conversion rates, click-through rates, or any other binary outcomes.
        
        Args:
            baseline_rate (float): The expected rate in the control group (0-1)
            mde (float): Minimum Detectable Effect as a proportion of baseline
            k (float): Ratio of treatment group size to control group size. Default is 1.
            is_two_sided (bool): Whether to use two-sided test. Default is True.
            
        Returns:
            int: Required sample size for the control group
            
        Example:
            >>> calculator = SampleSizeCalculator()
            >>> sample_size = calculator.calculate_binary_metric_sample_size(
            ...     baseline_rate=0.1,
            ...     mde=0.1
            ... )
        """
        z_alpha = self._get_critical_value(is_two_sided)
        var = baseline_rate * (1 - baseline_rate)
        delta = baseline_rate * mde
        
        n = (1/k * (baseline_rate + delta) * (1 - baseline_rate - delta) + var) * pow(z_alpha + self.z_beta, 2) / pow(delta, 2)
        return math.ceil(n)
    
    def calculate_continuous_metric_sample_size(self, data: pd.DataFrame, metric: str, mde: float, k: float = 1, is_two_sided: bool = True) -> int:
        """
        Calculate required sample size for continuous metrics (e.g., revenue, time spent).
        
        This method is suitable for metrics that follow a normal distribution,
        such as revenue per user, time spent on site, or any other continuous variable.
        
        Args:
            data (pd.DataFrame): Data containing the metric values
            metric (str): Name of the metric column in the dataframe
            mde (float): Minimum Detectable Effect as a proportion of baseline
            k (float): Ratio of treatment group size to control group size. Default is 1.
            is_two_sided (bool): Whether to use two-sided test. Default is True.
            
        Returns:
            int: Required sample size for the control group
            
        Example:
            >>> calculator = SampleSizeCalculator()
            >>> sample_size = calculator.calculate_continuous_metric_sample_size(
            ...     data=df,
            ...     metric='revenue',
            ...     mde=0.1
            ... )
        """
        z_alpha = self._get_critical_value(is_two_sided)
        baseline = np.mean(data[metric])
        variance = np.var(data[metric], ddof=1)
        effect_size = mde * baseline
        
        sample_size = ((1 + 1/k) * pow(z_alpha + self.z_beta, 2) * variance) / pow(effect_size, 2)
        return math.ceil(sample_size)
    
    def calculate_continuous_metric_sample_size_from_params(self, baseline_value: float, variance: float, mde: float, k: float = 1, is_two_sided: bool = True) -> int:
        """
        Calculate required sample size for continuous metrics using baseline value and variance directly.
        
        This is a convenience method that doesn't require a DataFrame.
        
        Args:
            baseline_value (float): The baseline/mean value of the metric
            variance (float): The variance of the metric
            mde (float): Minimum Detectable Effect as a proportion of baseline
            k (float): Ratio of treatment group size to control group size. Default is 1.
            is_two_sided (bool): Whether to use two-sided test. Default is True.
            
        Returns:
            int: Required sample size for the control group
        """
        z_alpha = self._get_critical_value(is_two_sided)
        effect_size = mde * baseline_value
        
        sample_size = ((1 + 1/k) * pow(z_alpha + self.z_beta, 2) * variance) / pow(effect_size, 2)
        return math.ceil(sample_size)
    
    def calculate_experiment_requirements(
        self,
        data: pd.DataFrame,
        metrics: List[Union[str, Tuple[str, str]]],
        metric_types: List[str],
        mde_range: Tuple[float, float, float],
        daily_traffic: int,
        sample_ratio: float,
        k: float = 1,
        group_num: int = 2,
        is_two_sided: bool = True
    ) -> pd.DataFrame:
        """
        Calculate comprehensive experiment requirements for multiple metrics and MDEs.
        
        This method provides a complete analysis of sample size requirements and
        experiment duration for multiple metrics across a range of MDEs.
        
        Args:
            data (pd.DataFrame): Data containing the metrics
            metrics (List[Union[str, Tuple[str, str]]]): List of metric names or (numerator, denominator) pairs
            metric_types (List[str]): List of metric types ('mean', 'proportion')
            mde_range (Tuple[float, float, float]): (start, end, step) for MDE range
            daily_traffic (int): Expected daily traffic
            sample_ratio (float): Ratio of traffic to include in experiment
            k (float): Ratio of treatment group proportion to control group proportion. Default is 1, meaning treatment group has the same proportion as control group.
            group_num (int): Number of experimental groups. Default is 2 (control + treatment).
            is_two_sided (bool): Whether to use two-sided test. Default is True.
            
        Returns:
            pd.DataFrame: DataFrame containing the following columns:
                - metric_name: Name of the metric
                - mde: Minimum Detectable Effect
                - control_sample_size: Required sample size for control group
                - treatment_sample_size: Required sample size for treatment group
                - total_sample_size: Total required sample size
                - experiment_days: Estimated number of days needed
            
        Example:
            >>> calculator = SampleSizeCalculator()
            >>> results_df = calculator.calculate_experiment_requirements(
            ...     data=df,
            ...     metrics=['revenue', 'conversion_rate', ('clicks', 'impressions')],
            ...     metric_types=['mean', 'proportion'],
            ...     mde_range=(0.01, 0.11, 0.01),
            ...     daily_traffic=10000,
            ...     sample_ratio=0.5
            ... )
            >>> print(results_df)
        """
        results = []
        start, end, step = mde_range
        
        for metric, metric_type in zip(metrics, metric_types):
            for mde in np.arange(start, end, step):
                if metric_type == 'mean':
                    control_sample = self.calculate_continuous_metric_sample_size(data, metric, mde, k, is_two_sided)
                elif metric_type == 'proportion':
                    baseline = np.mean(data[metric])
                    control_sample = self.calculate_binary_metric_sample_size(baseline, mde, k, is_two_sided)
                
                treated_sample = math.ceil(control_sample * k)
                total_sample = control_sample + treated_sample * (group_num - 1)
                exp_days = math.ceil(total_sample / (daily_traffic * sample_ratio))
                
                results.append({
                    'metric_name': str(metric),
                    'mde': mde,
                    'control_sample_size': control_sample,
                    'treatment_sample_size': treated_sample,
                    'total_sample_size': total_sample,
                    'experiment_days': exp_days
                })
        
        return pd.DataFrame(results)

