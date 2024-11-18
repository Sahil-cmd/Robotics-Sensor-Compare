# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# gui_main.py

import customtkinter as ctk
import signal

from sensor_tool.gui.gui_widgets import GUIWidgets
from sensor_tool.gui.gui_helpers import GUIHelpers


class SensorComparisonGUI(GUIWidgets, GUIHelpers):
    """
    A GUI application for comparing robotics sensors.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Robotics Sensor Compare Tool")
        self.root.geometry("1000x700")
        self.root.minsize(1000, 700)
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        self.auto_fill_var = ctk.BooleanVar()
        self.export_csv_var = ctk.BooleanVar()
        self.export_excel_var = ctk.BooleanVar()
        self.save_plot_var = ctk.BooleanVar()

        # Initialize base font size
        self.base_font_size = 14

        self.root.attributes("-alpha", 0.0)
        self.create_widgets()

        # Bind events
        self.root.bind("<Configure>", self.adjust_layout)
        self.root.protocol("WM_DELETE_WINDOW", self.quit_application)
        signal.signal(signal.SIGINT, self.handle_ctrl_c)

        self.fade_in()


def main():
    root = ctk.CTk()
    app = SensorComparisonGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
