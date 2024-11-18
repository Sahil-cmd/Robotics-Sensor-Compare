# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import pandas as pd
import numpy as np
import re
import logging


def format_label(label):
    """Formats a label by capitalizing words and handling special cases like 'RGB' and 'ROS'."""

    words = label.split("_")
    formatted_words = []
    for word in words:
        if word.upper() in ["RGB", "ROS"]:
            formatted_words.append(word.upper())
        else:
            formatted_words.append(word.capitalize())
    return " ".join(formatted_words)


def get_unit(attribute, sensor_data=None):
    """Retrieves the unit of measurement for a given attribute."""
    units = {
        "min_range": "m",
        "max_range": "m",
        "frame_rate": "FPS",
        "latency": "ms",
        "resolution_rgb": "pixels",
        "resolution_depth": "pixels",
        "field_of_view": "°",
        "power_consumption": "W",
        "weight": "g",
        "ros_compatibility_score": "",
        "price_avg": "USD",
    }
    if attribute in units:
        return units[attribute]
    else:
        unit_field = f"{attribute}_unit"
        if sensor_data is not None and unit_field in sensor_data:
            return sensor_data[unit_field]
        else:
            return ""


def is_higher_better(attribute):
    """Determines if a higher value is better for a given attribute."""
    higher_is_better = [
        "max_range",
        "frame_rate",
        "resolution_rgb",
        "resolution_depth",
        "field_of_view",
        "ros_compatibility_score",
    ]
    lower_is_better = [
        "min_range",
        "latency",
        "power_consumption",
        "weight",
        "price_avg",
    ]
    if attribute in higher_is_better:
        return True
    elif attribute in lower_is_better:
        return False
    else:
        return None


def extract_fov(value):
    """Extracts the field of view from a dictionary."""
    if isinstance(value, dict):
        if "diagonal" in value and pd.notna(value["diagonal"]):
            return value["diagonal"]
        elif "horizontal" in value and "vertical" in value:
            horizontal = value["horizontal"]
            vertical = value["vertical"]
            diagonal_fov = (horizontal**2 + vertical**2) ** 0.5
            return diagonal_fov
    return np.nan


def extract_resolution(resolution_dict, modality):
    """Extracts the resolution for a given modality (e.g., 'rgb', 'depth')."""
    if isinstance(resolution_dict, dict) and modality in resolution_dict:
        modality_res = resolution_dict[modality]
        if isinstance(modality_res, dict):
            width = modality_res.get("width")
            height = modality_res.get("height")
            if width and height:
                return width * height
    return np.nan


def extract_ros_compatibility(value):
    """Calculates the ROS compatibility score based on the supported ROS versions."""
    if not value:
        return np.nan
    if isinstance(value, list):
        value_list = value
    elif isinstance(value, str):
        value_list = [value]
    else:
        return np.nan
    score = 0
    if "ROS1" in value_list:
        score += 1
    if "ROS2" in value_list:
        score += 2
    return score


def extract_additional_ros_factors(sensor):
    """Calculates additional ROS compatibility score based on other factors."""
    score = 0
    factors = ["driver_maturity", "community_support", "documentation_quality"]
    max_score = len(factors) * 1
    for factor in factors:
        value = sensor.get(factor)
        if value is not None:
            score += value
    normalized_score = (score / max_score) * 2
    return normalized_score


def extract_numeric(value):
    """Extracts numeric value from a string or returns the value if already numeric."""
    if isinstance(value, str):
        numbers = re.findall(r"[-+]?\d*\.\d+|\d+", value)
        numbers = [float(num) for num in numbers]
        if numbers:
            return numbers[0]
    elif isinstance(value, (int, float)):
        return value
    else:
        return np.nan


def extract_price_avg(price_dict):
    """Calculates the average price from a price range dictionary."""
    if isinstance(price_dict, dict):
        min_price = price_dict.get("min_price")
        max_price = price_dict.get("max_price")
        if min_price and max_price:
            return (min_price + max_price) / 2
        elif min_price:
            return min_price
        elif max_price:
            return max_price
    return np.nan


def calculate_score(selected_sensors, attributes, weights):
    """Calculates a normalized score for each sensor based on attributes and weights."""
    scores = {}
    attribute_max = {}
    attribute_min = {}

    for attr in attributes:
        attribute_max[attr] = selected_sensors[attr].max()
        attribute_min[attr] = selected_sensors[attr].min()

    for idx, sensor in selected_sensors.iterrows():
        score = 0
        total_weight = 0
        for attr, weight in zip(attributes, weights):
            value = sensor[attr]
            if pd.notna(value):
                higher_better = is_higher_better(attr)
                total_weight += weight
                max_val = attribute_max[attr]
                min_val = attribute_min[attr]

                if higher_better is True and max_val != min_val:
                    normalized_value = (value - min_val) / (max_val - min_val)
                elif higher_better is False and max_val != min_val:
                    normalized_value = (max_val - value) / (max_val - min_val)
                else:
                    normalized_value = 0.5

                score += normalized_value * weight
            else:
                logging.warning(
                    f"Missing value for {attr} in sensor {sensor['sensor_id']}"
                )
        normalized_score = (score / total_weight) * 10 if total_weight > 0 else 0
        scores[sensor["sensor_id"]] = normalized_score

    return scores


def add_benchmark_line(
    ax, attribute, max_value, user_benchmark=None, user_benchmark_label=None
):
    """Adds a benchmark line to a plot."""
    color = "brown"
    if user_benchmark is not None:
        benchmark_value = user_benchmark
        label_text = user_benchmark_label
    else:
        default_benchmarks = {
            "frame_rate": 60,
            "latency": 50,
            "power_consumption": 10,
            "resolution_rgb": 1920 * 1080,
            "resolution_depth": 1280 * 720,
        }
        benchmark_value = default_benchmarks.get(attribute)
        label_text = str(benchmark_value)
    if benchmark_value is not None:
        label_map = {
            "frame_rate": f"Recommended Min. FPS: {label_text}",
            "latency": f"Recommended Max. Latency: {label_text} ms",
            "power_consumption": f"Recommended Max. Power: {label_text} W",
            "price_avg": f"Max Budget: {label_text} USD",
            "resolution_rgb": f"Recommended Resolution: {label_text} pixels",
            "resolution_depth": f"Recommended Resolution: {label_text} pixels",
        }
        label = label_map.get(
            attribute, f"Recommended {format_label(attribute)}: {label_text}"
        )
        ax.axhline(y=benchmark_value, color=color, linestyle="--", linewidth=1)
        ax.text(
            0, benchmark_value + (max_value * 0.02), label, color=color, fontsize=10
        )
