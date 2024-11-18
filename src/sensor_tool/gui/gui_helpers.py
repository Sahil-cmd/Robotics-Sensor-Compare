# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# gui_helpers.py

import customtkinter as ctk
import os
import re
import matplotlib
import openpyxl
import threading
from tkinter import messagebox, filedialog
import yaml

matplotlib.use("TkAgg")
from sensor_tool.visualize import visualize_comparison
from sensor_tool.data_loader import DataLoader
from sensor_tool import utils


class GUIHelpers:
    def adjust_layout(self, event):
        """
        Adjusts the font size and layout based on window resizing.

        Args:
            event (Event): The resize event.
        """

        new_font_size = min(
            18, max(self.base_font_size, int(self.root.winfo_width() / 80))
        )
        font = ("Helvetica", new_font_size, "bold")
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, ctk.CTkLabel) or isinstance(widget, ctk.CTkCheckBox):
                widget.configure(font=font)
            elif isinstance(widget, ctk.CTkEntry):
                widget.configure(font=("Helvetica", new_font_size))

        # Adjust font size for checkboxes in export_frame
        for widget in self.export_frame.winfo_children():
            if isinstance(widget, ctk.CTkCheckBox):
                widget.configure(font=font)

        # Adjust font size for buttons
        self.compare_button.configure(font=("Helvetica", new_font_size + 2, "bold"))
        self.quit_button.configure(font=("Helvetica", new_font_size + 2, "bold"))
        self.view_sensors_button.configure(font=("Helvetica", new_font_size))
        self.view_attributes_button.configure(font=("Helvetica", new_font_size))
        self.clear_fields_button.configure(font=("Helvetica", new_font_size))
        self.appearance_mode_switch.configure(font=("Helvetica", new_font_size))

    def fade_in(self):
        """
        Creates a fade-in effect when the application starts.
        """
        alpha = self.root.attributes("-alpha")
        if alpha < 1.0:
            alpha += 0.05
            self.root.attributes("-alpha", alpha)
            self.root.after(50, self.fade_in)
        else:
            self.root.attributes("-alpha", 1.0)

    def handle_ctrl_c(self, signum, frame):
        """
        Handles Ctrl+C signal to quit the application.
        """
        self.quit_application()

    def auto_fill_sample_data(self):
        """
        Auto-fills sample data for Sensor IDs and Attributes if checkbox is selected.
        """
        # Check if mandatory fields have data
        if self.auto_fill_var.get():
            if any([self.sensor_ids_entry.get(), self.attributes_entry.get()]):
                result = messagebox.askyesno(
                    "Confirm Auto-fill",
                    "Auto-filling will replace your current input data. Do you want to continue?",
                )
                if not result:
                    self.auto_fill_var.set(False)
                    return
            self.sensor_ids_entry.delete(0, "end")
            self.sensor_ids_entry.insert(0, "intel_realsense_d435i, stereolabs_zed_2")
            self.attributes_entry.delete(0, "end")
            self.attributes_entry.insert(0, "resolution_rgb, frame_rate, latency")
            self.weights_entry.delete(0, "end")
            self.weights_entry.insert(0, "0.4, 0.3, 0.3")
            self.benchmarks_entry.delete(0, "end")
            self.benchmarks_entry.insert(0, "1920x1080, 30, 50")

            # Enable the 'Start Comparison' button when auto-filled
            self.compare_button.configure(state="normal")
        else:
            # Clear fields and reset to placeholder text
            self.sensor_ids_entry.delete(0, "end")
            self.attributes_entry.delete(0, "end")
            self.weights_entry.delete(0, "end")
            self.benchmarks_entry.delete(0, "end")
            # Reset placeholder text
            self.sensor_ids_entry.configure(
                placeholder_text="e.g., intel_realsense_d435i, stereolabs_zed_2"
            )
            self.attributes_entry.configure(
                placeholder_text="e.g., resolution_rgb, frame_rate, latency"
            )
            self.weights_entry.configure(placeholder_text="e.g., 0.4, 0.3, 0.3")
            self.benchmarks_entry.configure(placeholder_text="e.g., 1920x1080, 30, 50")

            # Disable the 'Start Comparison' button when fields are cleared
            self.compare_button.configure(state="disabled")

    def show_available_sensors(self):
        """
        Displays the list of available sensors in a new window.
        """
        # Create a new Toplevel window
        self.sensor_window = ctk.CTkToplevel(self.root)
        self.sensor_window.title("Available Sensors")
        self.sensor_window.geometry("600x400")

        # Get the list of sensor IDs
        data_loader = DataLoader()
        df = data_loader.load_sensor_data()
        sensor_ids = df["sensor_id"].tolist()

        # Create a scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(self.sensor_window)
        scroll_frame.pack(fill="both", expand=True)

        # Create checkboxes for each sensor
        self.sensor_vars = {}
        for idx, sid in enumerate(sensor_ids):
            var = ctk.BooleanVar()
            chk = ctk.CTkCheckBox(
                scroll_frame,
                text=sid,
                variable=var,
                font=("Helvetica", self.base_font_size - 1),
                command=self.update_sensor_checkbox_states,
            )
            chk.pack(anchor="w", pady=2)
            self.sensor_vars[sid] = {"var": var, "chk": chk}

        # Confirm Selection Button
        confirm_button = ctk.CTkButton(
            self.sensor_window,
            text="Confirm Selection",
            command=self.confirm_sensor_selection,
            font=("Helvetica", self.base_font_size),
        )
        confirm_button.pack(pady=10)

        # Go Back Button
        back_button = ctk.CTkButton(
            self.sensor_window,
            text="Go Back",
            command=self.sensor_window.destroy,
            font=("Helvetica", self.base_font_size),
        )
        back_button.pack(pady=5)

    def update_sensor_checkbox_states(self):
        """
        Updates the state of sensor checkboxes based on the selection limit.
        """
        selected_count = sum(
            1 for sid in self.sensor_vars if self.sensor_vars[sid]["var"].get()
        )
        if selected_count >= 4:
            # Disable unselected checkboxes
            for sid in self.sensor_vars:
                if not self.sensor_vars[sid]["var"].get():
                    self.sensor_vars[sid]["chk"].configure(state="disabled")
        else:
            # Enable all checkboxes
            for sid in self.sensor_vars:
                self.sensor_vars[sid]["chk"].configure(state="normal")

    def confirm_sensor_selection(self):
        """
        Confirms the selected sensors and updates the sensor IDs entry field.
        """
        selected_sensors = [
            sid for sid in self.sensor_vars if self.sensor_vars[sid]["var"].get()
        ]
        if selected_sensors:
            self.sensor_ids_entry.delete(0, "end")
            self.sensor_ids_entry.insert(0, ", ".join(selected_sensors))
            self.validate_mandatory_fields()
        self.sensor_window.destroy()

    def get_available_attributes(self):
        """
        Retrieves the list of available attributes from the sensor schema.

        Returns:
            list: A list of attribute display names with units.
        """
        # Load sensor schema to get the list of attributes
        schema_path = os.path.join("config", "sensor_schema.yaml")
        with open(schema_path, "r") as f:
            schema = yaml.safe_load(f)

        exclude_keys = [
            "schema_version",
            "sensor_id",
            "manufacturer",
            "model",
            "sensor_type",
            "frame_rate_unit",
            "latency_unit",
            "driver_link_ros1",
            "driver_link_ros2",
            "github_repo",
            "key_features",
            "use_cases",
            "tags",
            "supported_platforms",
            "power_consumption_unit",
            "weight_unit",
            "sensor_image",
            "notes",
            "datasheet_link",
            "communication_interface",
            "environmental_rating",
        ]

        attributes = []
        for key in schema.keys():
            if key not in exclude_keys:
                if key == "resolution":
                    continue
                attributes.append(key)

        computed_attributes = ["resolution_rgb", "resolution_depth"]
        attributes.extend(computed_attributes)

        # Get units for each attribute
        attribute_list = []
        for attr in attributes:
            unit = utils.get_unit(attr)
            display_name = f"{attr} ({unit})" if unit else attr
            # display_name = f"{utils.format_label(attr)} ({unit})" if unit else utils.format_label(attr)
            attribute_list.append(display_name)
        return attribute_list

    def show_available_attributes(self):
        """
        Displays the list of available attributes in a new window.
        """
        # Create a new Toplevel window
        self.attribute_window = ctk.CTkToplevel(self.root)
        self.attribute_window.title("Available Attributes")
        self.attribute_window.geometry("600x400")

        # Get the list of attribute names from the sensor schema
        attributes = self.get_available_attributes()

        # Create a scrollable frame using CTkScrollableFrame
        scroll_frame = ctk.CTkScrollableFrame(self.attribute_window)
        scroll_frame.pack(fill="both", expand=True)

        # Create checkboxes for each attribute
        self.attribute_vars = {}
        for attr in attributes:
            var = ctk.BooleanVar()
            chk = ctk.CTkCheckBox(
                scroll_frame,
                text=attr,
                variable=var,
                font=("Helvetica", self.base_font_size - 1),
                command=self.update_attribute_checkbox_states,
            )
            chk.pack(anchor="w", pady=2)
            self.attribute_vars[attr] = {
                "var": var,
                "chk": chk,
            }

        # Confirm Selection Button
        confirm_button = ctk.CTkButton(
            self.attribute_window,
            text="Confirm Selection",
            command=self.confirm_attribute_selection,
            font=("Helvetica", self.base_font_size),
        )
        confirm_button.pack(pady=10)

        # Go Back Button
        back_button = ctk.CTkButton(
            self.attribute_window,
            text="Go Back",
            command=self.attribute_window.destroy,
            font=("Helvetica", self.base_font_size),
        )
        back_button.pack(pady=5)

    def update_attribute_checkbox_states(self):
        """
        Updates the state of attribute checkboxes based on the selection limit.
        """
        selected_count = sum(
            1 for attr in self.attribute_vars if self.attribute_vars[attr]["var"].get()
        )
        if selected_count >= 4:
            # Disable unselected checkboxes
            for attr in self.attribute_vars:
                if not self.attribute_vars[attr]["var"].get():
                    self.attribute_vars[attr]["chk"].configure(state="disabled")
        else:
            # Enable all checkboxes
            for attr in self.attribute_vars:
                self.attribute_vars[attr]["chk"].configure(state="normal")

    def confirm_attribute_selection(self):
        """
        Confirms the selected attributes and updates the attributes entry field.
        """
        selected_attributes = []
        for attr in self.attribute_vars:
            if self.attribute_vars[attr]["var"].get():
                # Strip units from attribute name
                attr_name = attr.split(" (")[0]
                selected_attributes.append(attr_name)
        if selected_attributes:
            self.attributes_entry.delete(0, "end")
            self.attributes_entry.insert(0, ", ".join(selected_attributes))
            self.validate_mandatory_fields()
        self.attribute_window.destroy()

    def clear_fields(self):
        """
        Resets all input fields to default values.
        """
        # Check if fields are not empty
        if any(
            [
                self.sensor_ids_entry.get(),
                self.attributes_entry.get(),
                self.weights_entry.get(),
                self.benchmarks_entry.get(),
            ]
        ):
            result = messagebox.askyesno(
                "Confirm Clear Fields",
                "Clearing fields will erase all your input data. Do you want to continue?",
            )
            if not result:
                return

        self.auto_fill_var.set(False)
        self.auto_fill_sample_data()
        # reset checkboxes
        self.export_csv_var.set(False)
        self.export_excel_var.set(False)
        self.save_plot_var.set(False)

    def process_optional_input(
        self, input_str, expected_length, input_name, parse_resolution=False
    ):
        """
        Helper function to process weights or benchmarks, with optional resolution parsing.

        Args:
            input_str (str): The input string.
            expected_length (int): Expected number of values.
            input_name (str): Name of the input field.
            parse_resolution (bool): Whether to parse resolution formats.

        Returns:
            tuple: A tuple of values and labels.
        """

        if input_str:
            try:
                values = []
                labels = []
                for x in input_str.split(","):
                    x = x.strip()
                    labels.append(x)
                    if parse_resolution and re.match(r"^\d+x\d+$", x):
                        width, height = map(int, x.lower().split("x"))
                        values.append(width * height)
                    elif parse_resolution and re.match(
                        r"^\d+\.?\d*\s*mp$", x, re.IGNORECASE
                    ):
                        mp_value = (
                            float(re.findall(r"\d+\.?\d*", x)[0]) * 1_000_000
                        )  # Convert MP to pixels
                        values.append(mp_value)
                    else:
                        try:
                            values.append(float(x))
                        except ValueError:
                            messagebox.showerror(
                                "Input Error",
                                f"{input_name} must be numeric or a valid resolution format.",
                            )
                            return None, None
                if len(values) != expected_length:
                    raise ValueError(
                        f"Number of {input_name} must match the number of attributes."
                    )
                return values, labels
            except ValueError as e:
                messagebox.showerror(
                    "Input Error",
                    f"{input_name.capitalize()} must be numeric or a valid resolution and match the attribute count.",
                )
                return None, None
        return None, None

    def execute_comparison(
        self,
        sensor_ids,
        attributes,
        weights,
        benchmarks,
        benchmark_labels,
        export_csv,
        export_excel,
        save_plot,
    ):
        """
        Executes the sensor comparison in a separate thread.

        Args:
            sensor_ids (list): List of sensor IDs.
            attributes (list): List of attributes.
            weights (list): List of weights.
            benchmarks (list): List of benchmark values.
            benchmark_labels (list): List of benchmark labels.
            export_csv (bool): Whether to export to CSV.
            export_excel (bool): Whether to export to Excel.
            save_plot (bool): Whether to save the plot.
        """
        try:
            # Call the visualization function
            visualize_comparison(
                sensor_ids=sensor_ids,
                attributes=attributes,
                weights=weights,
                benchmarks=benchmarks,
                benchmark_labels=benchmark_labels,
                save_plot=self.save_plot_path,
                export_csv=export_csv,
                export_csv_path=self.save_csv_path,
                export_excel=export_excel,
                export_excel_path=self.save_excel_path,
            )

            # Update progress bar to indicate completion
            self.root.after(0, self.progress_bar.set, 1.0)

            # Re-enable the "Start Comparison" button and hide progress bar
            self.root.after(0, self.compare_button.configure, {"state": "normal"})
            self.root.after(0, self.progress_bar.grid_remove)

            messagebox.showinfo("Success", "Comparison completed successfully.")

            # Show status messages
            messages = [
                "Comparison completed successfully. You can start a new comparison."
            ]
            if save_plot and self.save_plot_path:
                rel_path = os.path.relpath(self.save_plot_path)
                messages.append(f"Plot saved at '{rel_path}'")
            if export_csv and self.save_csv_path:
                rel_path = os.path.relpath(self.save_csv_path)
                messages.append(f"Comparison data exported to '{rel_path}'")
            if export_excel and self.save_excel_path:
                rel_path = os.path.relpath(self.save_excel_path)
                messages.append(f"Comparison data exported to '{rel_path}'")

            self.root.after(0, self.show_status_messages, messages)

        except Exception as e:
            self.root.after(0, self.compare_button.configure, {"state": "normal"})
            self.root.after(0, self.progress_bar.grid_remove)
            self.root.after(
                0, lambda e=e: messagebox.showerror("Error", f"An error occurred: {e}")
            )

    def run_comparison(self):
        """
        Retrieves input values and starts the sensor comparison.
        """
        sensor_ids = [
            sid.strip() for sid in self.sensor_ids_entry.get().split(",") if sid.strip()
        ]
        attributes = [
            attr.strip()
            for attr in self.attributes_entry.get().split(",")
            if attr.strip()
        ]

        # Input validation
        if not sensor_ids or len(sensor_ids) < 2:
            messagebox.showerror("Input Error", "Please enter at least two sensor IDs.")
            return
        if not attributes:
            messagebox.showerror("Input Error", "Please enter at least one attribute.")
            return

        # Process weights
        weights_input = self.weights_entry.get()
        weights, _ = self.process_optional_input(
            weights_input, len(attributes), "weights"
        )
        if weights_input and weights is None:
            return

        # Process benchmarks
        benchmarks_input = self.benchmarks_entry.get()
        benchmarks, benchmark_labels = self.process_optional_input(
            benchmarks_input, len(attributes), "benchmarks", parse_resolution=True
        )
        if benchmarks_input and benchmarks is None:
            return

        export_csv = self.export_csv_var.get()
        export_excel = self.export_excel_var.get()
        save_plot = self.save_plot_var.get()

        # Initialize paths
        self.save_plot_path = None
        self.save_csv_path = None
        self.save_excel_path = None

        if save_plot:
            self.save_plot_path = filedialog.asksaveasfilename(
                defaultextension=".png", filetypes=[("PNG Files", "*.png")]
            )
            if not self.save_plot_path:
                return

        if export_csv:
            self.save_csv_path = filedialog.asksaveasfilename(
                defaultextension=".csv", filetypes=[("CSV Files", "*.csv")]
            )
            if not self.save_csv_path:
                return

        if export_excel:
            self.save_excel_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")]
            )
            if not self.save_excel_path:
                return

        # Disable the "Start Comparison" button and show progress bar
        self.compare_button.configure(state="disabled")
        self.progress_bar.grid()
        self.progress_bar.set(0.3)

        # Run the comparison in a separate thread
        threading.Thread(
            target=self.execute_comparison,
            args=(
                sensor_ids,
                attributes,
                weights,
                benchmarks,
                benchmark_labels,
                export_csv,
                export_excel,
                save_plot,
            ),
            daemon=True,
        ).start()

    def show_status_messages(self, messages):
        """
        Displays status messages to the user.
        """
        # Clear existing status labels
        for lbl in self.status_labels:
            lbl.destroy()
        self.status_labels.clear()

        for idx, message in enumerate(messages):
            status_label = ctk.CTkLabel(
                self.main_frame,
                text=message,
                font=("Helvetica", self.base_font_size),
                text_color="green",
            )
            status_label.grid(row=10 + idx, column=0, columnspan=2, padx=20, pady=5)
            self.status_labels.append(status_label)
            # Schedule to clear each message after a few seconds
            self.root.after(5000, status_label.destroy)

    def toggle_appearance_mode(self):
        """
        Toggles between Dark and Light modes.
        """
        if self.appearance_mode_switch.get():
            ctk.set_appearance_mode("Dark")
            self.appearance_mode_switch.configure(text="Dark Mode")
        else:
            ctk.set_appearance_mode("Light")
            self.appearance_mode_switch.configure(text="Light Mode")

    def validate_mandatory_fields(self, event=None):
        """
        Validates mandatory fields and enables/disables the compare button.

        Args:
            event (Event, optional): The key release event.
        """
        if self.sensor_ids_entry.get().strip() and self.attributes_entry.get().strip():
            self.compare_button.configure(state="normal")
        else:
            self.compare_button.configure(state="disabled")

    def fade_out(self):
        """
        Creates a fade-out effect when the application closes.
        """
        alpha = self.root.attributes("-alpha")
        if alpha > 0:
            alpha -= 0.1
            self.root.attributes("-alpha", alpha)
            self.root.after(30, self.fade_out)
        else:
            self.root.destroy()

    def quit_application(self):
        """
        Confirms exit and displays a message before quitting.
        """
        result = messagebox.askyesno("Confirm Exit", "Are you sure you want to exit?")
        if result:
            self.fade_out()
