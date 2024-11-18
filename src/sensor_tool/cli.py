# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse

from sensor_tool.visualize import visualize_comparison
from sensor_tool.filter_sensors import filter_sensors
from sensor_tool.validate_sensors import validate_sensors_main


def main():
    parser = argparse.ArgumentParser(description="Sensor Comparison Tool CLI")
    subparsers = parser.add_subparsers(dest="command")

    visualize_parser = subparsers.add_parser(
        "visualize", help="Visualize and compare sensor attributes"
    )

    visualize_parser.add_argument(
        "--sensor_ids",
        nargs="+",
        required=True,
        help="List of sensor IDs to compare (at least two)",
    )
    visualize_parser.add_argument(
        "--attributes",
        nargs="+",
        required=True,
        help="Attributes to compare (e.g., min_range, max_range, frame_rate)",
    )
    visualize_parser.add_argument(
        "--weights",
        nargs="+",
        type=float,
        help="Weights for each attribute (optional, default is equal weights)",
    )
    visualize_parser.add_argument(
        "--benchmarks",
        nargs="+",
        type=float,
        help="Custom benchmark values for each attribute (optional)",
    )
    visualize_parser.add_argument(
        "--save_plot",
        action="store_true",
        help="Save the plot to a file instead of displaying it",
    )
    visualize_parser.add_argument(
        "--export_csv", action="store_true", help="Export comparison data to CSV"
    )
    visualize_parser.add_argument(
        "--export_excel", action="store_true", help="Export comparison data to Excel"
    )

    filter_parser = subparsers.add_parser(
        "filter", help="Filter sensors based on criteria"
    )
    filter_parser.add_argument(
        "--sensor_type", help="Type of sensor (e.g., 'RGB Camera', 'LiDAR')"
    )
    filter_parser.add_argument(
        "--manufacturer", help="Name of the manufacturer (e.g., 'Intel')"
    )
    filter_parser.add_argument(
        "--min_resolution", type=int, help="Minimum resolution in pixels"
    )
    filter_parser.add_argument(
        "--max_resolution", type=int, help="Maximum resolution in pixels"
    )
    filter_parser.add_argument(
        "--min_frame_rate", type=float, help="Minimum frame rate in FPS"
    )
    filter_parser.add_argument(
        "--max_frame_rate", type=float, help="Maximum frame rate in FPS"
    )
    filter_parser.add_argument("--min_price", type=float, help="Minimum price in USD")
    filter_parser.add_argument("--max_price", type=float, help="Maximum price in USD")
    filter_parser.add_argument(
        "--min_fov", type=float, help="Minimum field of view in degrees"
    )
    filter_parser.add_argument(
        "--max_fov", type=float, help="Maximum field of view in degrees"
    )
    filter_parser.add_argument(
        "--ros_compatibility", help="ROS compatibility version (e.g., 'ROS1', 'ROS2')"
    )

    validate_parser = subparsers.add_parser(
        "validate", help="Validate sensor data files against schema"
    )
    validate_parser.add_argument(
        "files", nargs="*", help="Sensor YAML files to validate"
    )

    gui_parser = subparsers.add_parser("gui", help="Launch the GUI application")

    args = parser.parse_args()

    if args.command == "visualize":
        visualize_comparison(
            sensor_ids=args.sensor_ids,
            attributes=args.attributes,
            weights=args.weights,
            benchmarks=args.benchmarks,
            save_plot=args.save_plot,
            export_csv=args.export_csv,
            export_excel=args.export_excel,
        )
    elif args.command == "filter":
        filtered_df = filter_sensors(
            sensor_type=args.sensor_type,
            manufacturer=args.manufacturer,
            ros_compatibility=args.ros_compatibility,
            min_resolution=args.min_resolution,
            max_resolution=args.max_resolution,
            min_frame_rate=args.min_frame_rate,
            max_frame_rate=args.max_frame_rate,
            min_price=args.min_price,
            max_price=args.max_price,
            min_fov=args.min_fov,
            max_fov=args.max_fov,
        )
        print(
            filtered_df[
                [
                    "sensor_id",
                    "sensor_type",
                    "manufacturer",
                    "model",
                    "ros_compatibility",
                    "resolution_rgb",
                    "frame_rate",
                    "price_avg",
                    "field_of_view",
                ]
            ]
        )

    elif args.command == "validate":
        validate_sensors_main(args.files)

    elif args.command == "gui":
        from sensor_tool.gui import main as gui_main

        gui_main()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
