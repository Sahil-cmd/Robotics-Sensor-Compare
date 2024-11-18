# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from .data_loader import DataLoader
from .utils import extract_numeric, extract_resolution


def filter_sensors(
    sensor_type=None,
    manufacturer=None,
    ros_compatibility=None,
    min_resolution=None,
    max_resolution=None,
    min_frame_rate=None,
    max_frame_rate=None,
    min_price=None,
    max_price=None,
    min_fov=None,
    max_fov=None,
):

    data_loader = DataLoader()
    df = data_loader.load_sensor_data()

    # Extract and preprocess necessary data
    df["resolution_rgb"] = df["resolution"].apply(
        lambda x: extract_resolution(x, "rgb")
    )
    df["field_of_view"] = df["field_of_view"].apply(extract_numeric)
    df["frame_rate"] = df["frame_rate"].apply(extract_numeric)
    df["price_avg"] = df["price_range"].apply(
        lambda x: x.get("avg") if isinstance(x, dict) else None
    )

    # Apply filters
    if sensor_type:
        df = df[df["sensor_type"].str.contains(sensor_type, case=False, na=False)]
    if manufacturer:
        df = df[df["manufacturer"].str.contains(manufacturer, case=False, na=False)]
    if min_resolution:
        df = df[df["resolution_rgb"] >= min_resolution]
    if max_resolution:
        df = df[df["resolution_rgb"] <= max_resolution]
    if min_frame_rate:
        df = df[df["frame_rate"] >= min_frame_rate]
    if max_frame_rate:
        df = df[df["frame_rate"] <= max_frame_rate]
    if min_price:
        df = df[df["price_avg"] >= min_price]
    if max_price:
        df = df[df["price_avg"] <= max_price]
    if min_fov:
        df = df[df["field_of_view"] >= min_fov]
    if max_fov:
        df = df[df["field_of_view"] <= max_fov]
    if ros_compatibility:
        df = df[
            df["ros_compatibility"].apply(
                lambda x: ros_compatibility in x if isinstance(x, list) else False
            )
        ]

    return df
