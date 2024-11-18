import os

LICENSE_TEXT = '''# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''

def add_license_header(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    if LICENSE_TEXT.strip() not in content:
        with open(file_path, 'w') as f:
            f.write(LICENSE_TEXT + content)

for root, dirs, files in os.walk('src'):
    for file in files:
        if file.endswith('.py'):
            file_path = os.path.join(root, file)
            add_license_header(file_path)
