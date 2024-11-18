# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import yaml
import pandas as pd


class DataLoader:
    def __init__(self, sensors_directory="sensors"):
        self.sensors_directory = sensors_directory

    def load_sensor_data(self):
        sensor_data = []
        for root, _, files in os.walk(self.sensors_directory):
            for file in files:
                if file.endswith(".yaml"):
                    with open(os.path.join(root, file), "r") as f:
                        sensor = yaml.safe_load(f)
                        sensor_data.append(sensor)
        return pd.DataFrame(sensor_data)
