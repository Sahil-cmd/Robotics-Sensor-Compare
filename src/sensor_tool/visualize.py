# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import logging
import sys
from matplotlib.patches import Patch
from .data_loader import DataLoader
from . import utils


def visualize_comparison(
    sensor_ids,
    attributes,
    weights=None,
    benchmarks=None,
    benchmark_labels=None,
    save_plot=None,
    export_csv=False,
    export_excel=False,
    export_csv_path=None,
    export_excel_path=None,
):
    """Visualizes and compares sensor attributes.

    Args:
        sensor_ids (list): List of sensor IDs to compare.
        attributes (list): Attributes to compare.
        weights (list, optional): Weights for each attribute.
        benchmarks (list, optional): Benchmark values for each attribute.
        benchmark_labels (list, optional): Labels for benchmark values.
        save_plot (str, optional): Path to save the plot.
        export_csv (bool, optional): Whether to export data to CSV.
        export_excel (bool, optional): Whether to export data to Excel.
        export_csv_path (str, optional): Path to save CSV file.
        export_excel_path (str, optional): Path to save Excel file.

    Returns:
        None
    """
    data_loader = DataLoader()
    df = data_loader.load_sensor_data()

    # Preprocess data
    df["ros_compatibility_score"] = df["ros_compatibility"].apply(
        utils.extract_ros_compatibility
    )
    df["additional_ros_score"] = df.apply(utils.extract_additional_ros_factors, axis=1)
    df["ros_total_score"] = df["ros_compatibility_score"] + df["additional_ros_score"]

    df["resolution"] = df["resolution"].apply(
        lambda x: x if isinstance(x, dict) else {}
    )
    if "resolution_rgb" in attributes:
        df["resolution_rgb"] = df["resolution"].apply(
            lambda x: utils.extract_resolution(x, "rgb")
        )
    if "resolution_depth" in attributes:
        df["resolution_depth"] = df["resolution"].apply(
            lambda x: utils.extract_resolution(x, "depth")
        )

    if "field_of_view" in attributes:
        df["field_of_view"] = df["field_of_view"].apply(utils.extract_fov)

    if "price_avg" in attributes:
        df["price_avg"] = df["price_range"].apply(utils.extract_price_avg)

    for attr in attributes:
        if attr in [
            "ros_compatibility_score",
            "ros_total_score",
            "additional_ros_score",
            "resolution_rgb",
            "resolution_depth",
            "field_of_view",
            "price_avg",
        ]:
            continue
        if attr not in df.columns:
            logging.error(f"Attribute {attr} not found in data.")
            sys.exit(1)
        df[attr] = df[attr].apply(utils.extract_numeric)

    selected_sensors = df[df["sensor_id"].isin(sensor_ids)]
    selected_sensors = selected_sensors.reset_index(drop=True)

    if selected_sensors.empty:
        logging.error("No matching sensors found in the database.")
        return

    if len(selected_sensors) < 2:
        logging.error("At least two sensors must be specified for a comparison.")
        sys.exit(1)

    if weights is None:
        weights = [1.0] * len(attributes)

    if len(weights) != len(attributes):
        logging.error("Number of weights must match the number of attributes.")
        sys.exit(1)

    num_attributes = len(attributes)
    cols = 2
    rows = (num_attributes + cols - 1) // cols
    fig, axes = plt.subplots(nrows=rows, ncols=cols, figsize=(14, 5 * rows))
    fig.canvas.manager.set_window_title("Sensor Comparison Results")

    axes = axes.flatten()

    dark_blue_used = False

    for i, attribute in enumerate(attributes):
        ax = axes[i] if num_attributes > 1 else axes

        higher_better = utils.is_higher_better(attribute)
        values = selected_sensors[attribute]

        max_value = values.max()
        min_value = values.min()
        y_max = max_value * 1.2 if pd.notna(max_value) else 1
        ax.set_ylim(0, y_max)

        colors = []

        if values.isnull().all():
            colors = ["gray"] * len(values)
        elif len(values.dropna().unique()) == 1:
            colors = ["gray"] * len(values)
        elif len(values) == 2:
            for value in values:
                if pd.isna(value):
                    colors.append("gray")
                else:
                    if higher_better is True:
                        colors.append("green" if value == max_value else "red")
                    elif higher_better is False:
                        colors.append("green" if value == min_value else "red")
                    else:
                        colors.append("gray")
            dark_blue_used = False
        else:
            for value in values:
                if pd.isna(value):
                    colors.append("gray")
                else:
                    if higher_better is True:
                        if value == max_value:
                            colors.append("green")
                        elif value == min_value:
                            colors.append("red")
                        else:
                            colors.append("#00008B")
                            dark_blue_used = True
                    elif higher_better is False:
                        if value == min_value:
                            colors.append("green")
                        elif value == max_value:
                            colors.append("red")
                        else:
                            colors.append("#00008B")
                            dark_blue_used = True
                    else:
                        colors.append("#00008B")
                        dark_blue_used = True

        bar_width = 0.4
        x_positions = np.arange(len(selected_sensors))
        bars = ax.bar(
            x_positions,
            values.fillna(0),
            color=colors,
            edgecolor="black",
            alpha=0.7,
            width=bar_width,
        )

        for bar, value in zip(bars, values):
            if pd.notna(value):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    value + (y_max * 0.02),
                    f"{value:.2f}",
                    ha="center",
                    va="bottom",
                    fontsize=10,
                    color="black",
                )
            else:
                bar_height = y_max * 0.05
                bar.set_height(bar_height)
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    y_max * 0.05,
                    "N/A",
                    ha="center",
                    va="bottom",
                    fontsize=11,
                    color="black",
                )
                bar.set_color("gray")

        ax.set_title(f"Comparison of {utils.format_label(attribute)}", fontsize=14)
        ax.set_xlabel("Sensor", fontsize=12)
        unit = utils.get_unit(attribute)
        ylabel = (
            f"{utils.format_label(attribute)} ({unit})"
            if unit
            else utils.format_label(attribute)
        )
        ax.set_ylabel(ylabel, fontsize=12)
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        ax.set_xticks(x_positions)
        ax.set_xticklabels(
            [utils.format_label(label) for label in selected_sensors["sensor_id"]],
            rotation=0,
        )

        if benchmarks and i < len(benchmarks):
            user_benchmark_value = benchmarks[i]
            user_benchmark_label = benchmark_labels[i]
        else:
            user_benchmark_value = None
            user_benchmark_label = None
        utils.add_benchmark_line(
            ax, attribute, y_max, user_benchmark_value, user_benchmark_label
        )

    for j in range(num_attributes, len(axes)):
        fig.delaxes(axes[j])

    legend_elements = [
        Patch(facecolor="green", edgecolor="black", label="Higher Performance"),
        Patch(facecolor="red", edgecolor="black", label="Lower Performance"),
    ]

    if dark_blue_used:
        legend_elements.append(
            Patch(facecolor="#00008B", edgecolor="black", label="Average Performance")
        )

    legend_elements.append(
        Patch(facecolor="gray", edgecolor="black", label="Data Not Available")
    )

    axes[0].legend(handles=legend_elements, loc="upper right")

    scores = utils.calculate_score(selected_sensors, attributes, weights)
    print("\nSensor Scores (Higher is better overall):")
    for sensor_id in selected_sensors["sensor_id"]:
        score = scores.get(sensor_id, "N/A")
        if score != "N/A":
            print(f"{sensor_id}: {score:.2f}/10")
        else:
            print(f"{sensor_id}: Score not available (missing data)")

    plt.tight_layout()

    if save_plot:
        plt.savefig(save_plot)
        logging.info(f"Plot saved to '{save_plot}'")
    else:
        plt.show()

    if export_csv and export_csv_path:
        selected_data = selected_sensors[["sensor_id"] + attributes]
        selected_data.to_csv(export_csv_path, index=False)
        logging.info(f"Comparison data exported to {export_csv_path}")

    if export_excel and export_excel_path:
        selected_data = selected_sensors[["sensor_id"] + attributes]
        selected_data.to_excel(export_excel_path, index=False)
        logging.info(f"Comparison data exported to {export_excel_path}")
