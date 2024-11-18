# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# gui_widgets.py


import customtkinter as ctk


class GUIWidgets:
    def create_widgets(self):
        """
        Creates and arranges all the widgets in the GUI.
        """

        # Main frame for layout
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=15)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        for i in range(15):
            self.main_frame.grid_rowconfigure(i, weight=1)
        self.main_frame.grid_columnconfigure((0, 1), weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

        # Input fields
        self.add_label_and_entry(
            "Sensor IDs (comma-separated):",
            "e.g., intel_realsense_d435i, stereolabs_zed_2",
            row=0,
            mandatory=True,
        )
        self.add_label_and_entry(
            "Attributes (comma-separated):",
            "e.g., resolution_rgb, frame_rate, latency",
            row=1,
            mandatory=True,
        )
        self.add_label_and_entry(
            "Weights (optional, comma-separated):", "e.g., 0.4, 0.3, 0.3", row=2
        )
        self.add_label_and_entry(
            "Benchmarks (optional, comma-separated):", "e.g., 1920x1080, 30, 50", row=3
        )

        self.create_additional_buttons()
        self.create_export_options()
        self.create_action_buttons()
        self.create_appearance_mode_switch()

        # Status Labels
        self.status_labels = []

    def add_label_and_entry(self, label_text, placeholder_text, row, mandatory=False):
        """
        Helper function to add a label and entry field to the main frame.
        """
        if mandatory:
            label_text += "*"

        label = ctk.CTkLabel(
            self.main_frame,
            text=label_text,
            font=("Helvetica", self.base_font_size, "bold"),
        )
        label.grid(row=row, column=0, padx=20, pady=10, sticky="w")
        entry = ctk.CTkEntry(
            self.main_frame,
            width=500,
            placeholder_text=placeholder_text,
            font=("Helvetica", self.base_font_size),
        )
        entry.grid(row=row, column=1, padx=20, pady=10, sticky="we")
        self.main_frame.grid_columnconfigure(1, weight=1)
        if row == 0:
            self.sensor_ids_entry = entry
            self.sensor_ids_entry.bind("<KeyRelease>", self.validate_mandatory_fields)
        elif row == 1:
            self.attributes_entry = entry
            self.attributes_entry.bind("<KeyRelease>", self.validate_mandatory_fields)
        elif row == 2:
            self.weights_entry = entry
        elif row == 3:
            self.benchmarks_entry = entry

    def create_additional_buttons(self):
        """
        Creates additional buttons like 'View Available Sensors' and 'Clear Fields'.
        """

        buttons_frame = ctk.CTkFrame(self.main_frame)
        buttons_frame.grid(row=4, column=1, columnspan=2, pady=5, sticky="we")
        buttons_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.view_sensors_button = ctk.CTkButton(
            buttons_frame,
            text="View Available Sensors",
            command=self.show_available_sensors,
            font=("Helvetica", self.base_font_size),
            corner_radius=10,
            height=40,
        )
        self.view_sensors_button.grid(row=0, column=0, padx=10, pady=5, sticky="we")

        self.view_attributes_button = ctk.CTkButton(
            buttons_frame,
            text="View Available Attributes",
            command=self.show_available_attributes,
            font=("Helvetica", self.base_font_size),
            corner_radius=10,
            height=40,
        )
        self.view_attributes_button.grid(row=0, column=1, padx=10, pady=5, sticky="we")

        self.clear_fields_button = ctk.CTkButton(
            buttons_frame,
            text="Clear Fields",
            command=self.clear_fields,
            font=("Helvetica", self.base_font_size),
            corner_radius=10,
            width=140,
            height=40,
        )
        self.clear_fields_button.grid(row=0, column=2, padx=10, pady=5, sticky="we")

        reset_label = ctk.CTkLabel(
            buttons_frame,
            text="Resets to default values",
            font=("Helvetica", int(self.base_font_size * 0.8)),
            text_color="gray",
        )
        reset_label.grid(row=1, column=2, padx=10, pady=0)

    def create_export_options(self):
        """
        Creates export and save options checkboxes.
        """

        self.export_frame = ctk.CTkFrame(self.main_frame)
        self.export_frame.grid(row=5, column=1, columnspan=2, pady=20, sticky="w")

        export_options = [
            ("Auto-fill sample data", self.auto_fill_var, self.auto_fill_sample_data),
            ("Export to CSV", self.export_csv_var, None),
            ("Export to Excel", self.export_excel_var, None),
            ("Save Plot to File", self.save_plot_var, None),
        ]

        for idx, (text, var, cmd) in enumerate(export_options):
            chk = ctk.CTkCheckBox(
                self.export_frame,
                text=text,
                variable=var,
                command=cmd,
                font=("Helvetica", self.base_font_size),
            )
            chk._text_label.configure(pady=5)
            chk.grid(row=idx, column=0, sticky="w", padx=10, pady=5)

    def create_action_buttons(self):
        """
        Creates main action buttons like 'Start Comparison' and 'Quit'.
        """

        self.compare_button = ctk.CTkButton(
            self.main_frame,
            text="Start Comparison",
            command=self.run_comparison,
            font=("Helvetica", self.base_font_size + 2, "bold"),
            corner_radius=15,
            fg_color="#1f6aa5",
            hover_color="#144870",
            height=50,
        )
        self.compare_button.grid(row=6, column=1, padx=20, pady=20, sticky="we")
        self.compare_button.configure(state="disabled")

        self.progress_bar = ctk.CTkProgressBar(self.main_frame)
        self.progress_bar.grid(
            row=7, column=0, columnspan=2, padx=20, pady=10, sticky="we"
        )
        self.progress_bar.set(0)
        self.progress_bar.grid_remove()

        self.quit_button = ctk.CTkButton(
            self.main_frame,
            text="Quit",
            command=self.quit_application,
            font=("Helvetica", self.base_font_size, "bold"),
            corner_radius=10,
            fg_color="#a51f1f",
            hover_color="#701414",
            height=50,
        )
        self.quit_button.grid(row=6, column=0, padx=20, pady=20, sticky="we")

    def create_appearance_mode_switch(self):
        """
        Creates the appearance mode switch.
        """

        appearance_frame = ctk.CTkFrame(self.main_frame)
        appearance_frame.grid(row=8, column=1, pady=10, sticky="e")

        appearance_label = ctk.CTkLabel(
            appearance_frame,
            text="Appearance Mode:",
            font=("Helvetica", self.base_font_size),
        )
        appearance_label.grid(row=0, column=0, padx=10, pady=5)

        self.appearance_mode_switch = ctk.CTkSwitch(
            appearance_frame,
            text="Dark Mode",
            command=self.toggle_appearance_mode,
            font=("Helvetica", self.base_font_size),
        )
        self.appearance_mode_switch.grid(row=0, column=1, padx=10, pady=5)
        self.appearance_mode_switch.select()  # Default to Dark Mode

        mandatory_label = ctk.CTkLabel(
            self.main_frame,
            text="Fields marked with * are mandatory",
            font=("Helvetica", int(self.base_font_size * 0.8)),
            text_color="gray",
        )
        mandatory_label.grid(row=9, column=0, columnspan=2, padx=20, pady=10)
