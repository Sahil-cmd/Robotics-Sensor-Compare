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
import sys
import logging
import yamale


def get_schema_path():
    """Returns the path to the sensor schema file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    schema_dir = os.path.join(repo_root, "config")
    schema_file = "sensor_schema.yaml"
    schema_path = os.path.join(schema_dir, schema_file)

    if os.path.exists(schema_path):
        return schema_path
    else:
        logging.error(f"Schema file not found at {schema_path}.")
        return None


def validate_sensor(file_path, schema):
    """Validates a sensor YAML file against the schema."""
    try:
        data = yamale.make_data(file_path)
        yamale.validate(schema, data)
        logging.info(f"{file_path} is valid.")
        return True
    except yamale.YamaleError as e:
        logging.error(f"Validation failed for {file_path}:")
        for result in e.results:
            for error in result.errors:
                logging.error(f" - {error}")
        return False
    except Exception as e:
        logging.error(f"An error occurred while validating {file_path}: {e}")
        return False


def validate_sensors_main(files=[]):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    schema_path = get_schema_path()
    if schema_path is None:
        sys.exit(1)

    try:
        schema = yamale.make_schema(schema_path)
    except Exception as e:
        logging.error(f"Failed to load schema from {schema_path}: {e}")
        sys.exit(1)

    if files:
        for file_path in files:
            if os.path.isfile(file_path):
                validate_sensor(file_path, schema)
            else:
                logging.warning(f"File not found: {file_path}")
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
        sensors_dir = os.path.join(repo_root, "sensors")

        for root, _, files in os.walk(sensors_dir):
            for file in files:
                if file.endswith(".yaml"):
                    file_path = os.path.join(root, file)
                    validate_sensor(file_path, schema)
