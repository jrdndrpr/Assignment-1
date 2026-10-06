import os

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator


class BioprocessMonitor:
    def __init__(self, filepath, ph_lims, temperature_lims):
        """
        Utility class used to monitor bioprocesses by
        generating dashboards and summaries.

        Parameters
        ----------
        filepath : str
            Input CSV dataset path.
        ph_lims : tuple[float, float]
            Lower and upper acceptable pH limits.
        temperature_lims : tuple[float, float]
            Lower and upper acceptable temperature limits.
        """

        self.filepath = filepath
        self.ph_lims = ph_lims
        self.temperature_lims = temperature_lims

        self.df = pd.read_csv(self.filepath)

    def extract_batch(self, batch_id):
        """
        Extracts data corresponding to a single batch.

        Parameters
        ----------
        batch_id : int
            Batch identifier.

        Returns
        -------
        pandas.DataFrame
            DataFrame containing only rows associated with
            the requested batch.
        """

        mask = self.df.loc[:, "batch_id"] == batch_id
        return self.df.loc[mask, :].copy()

    def optimal_ph_mask(self, df_batch):
        """
        Determines whether each pH measurement falls within
        the acceptable operating range.

        Parameters
        ----------
        df_batch : pandas.DataFrame
            Batch-specific DataFrame.

        Returns
        -------
        array-like of bool
            A mask whereby True indicates that the measurement
            is within the acceptable operating range.
        """

        ph_vals = df_batch.loc[:, "pH"].to_numpy()
        mask_ph = (ph_vals >= self.ph_lims[0]) & (ph_vals <= self.ph_lims[1])

        return mask_ph

    def optimal_temperature_mask(self, df_batch):
        """
        Determines whether each temperature measurement falls
        within the acceptable operating range.

        Parameters
        ----------
        df_batch : pandas.DataFrame
            Batch-specific DataFrame.

        Returns
        -------
        array-like of bool
            A mask whereby True indicates that the measurement
            is within the acceptable operating range.
        """

        temp_vals = df_batch.loc[:, "temperature_C"].to_numpy()
        mask_temp = (temp_vals >= self.temperature_lims[0]) & (
            temp_vals <= self.temperature_lims[1]
        )

        return mask_temp

    def get_n_batches(self):
        """
        Determines the number of unique batches present
        in the dataset.

        Returns
        -------
        int
            Total number of distinct batch identifiers.
        """

        batch_ids = self.df.loc[:, "batch_id"].to_numpy()
        unique_batch = np.unique(batch_ids)

        return len(unique_batch)

    def export_dashboard(self, batch_id, filepath):
        """
        Creates and saves a dashboard figure for a single batch.

        Parameters
        ----------
        batch_id : int
            Batch identifier.
        filepath : str
            Output PNG image path.

        Dashboard Requirements
        ----------------------
        Create a 2 × 2 figure containing:

        Top-Left
            Glucose, biomass, and product concentrations versus time.
            - A different color and marker should be used for each substance.

        Top-Right
            Temperature versus time.
            - Measurements within the acceptable temperature range
              should be displayed as green circles.
            - Measurements outside the acceptable temperature range
              should be displayed as red X markers.

        Bottom-Left
            pH versus time.
            - Measurements within the acceptable pH range
              should be displayed as green circles.
            - Measurements outside the acceptable pH range
              should be displayed as red X markers.

        Bottom-Right
            Dissolved oxygen versus time.

        Additional Requirements
        ----------------------
        - Use scatter plots.
        - Add x-axis and y-axis labels.
        - Add legends where appropriate.
        - Apply consistent formatting across all subplots unless
          indicated otherwise.
        - Apply a tick spacing of 6 h on the x-axis for all subplots.
        - Save the figure to the provided filepath.
        - Close the figure after saving.
        """

        df_batch = self.extract_batch(batch_id)

        time_vals = df_batch.loc[:, "time_h"].to_numpy()
        temp_vals = df_batch.loc[:, "temperature_C"].to_numpy()
        ph_vals = df_batch.loc[:, "pH"].to_numpy()
        do_vals = df_batch.loc[:, "DO_percent"].to_numpy()

        c_glucose = df_batch.loc[:, "C_glucose_g_L^-1"].to_numpy()
        c_biomass = df_batch.loc[:, "C_biomass_g_L^-1"].to_numpy()
        c_product = df_batch.loc[:, "C_product_g_L^-1"].to_numpy()

        temp_mask = self.optimal_temperature_mask(df_batch)
        ph_mask = self.optimal_ph_mask(df_batch)

        fig, ax = plt.subplots(
            2,
            2,
            figsize=(6.5, 4.0),
            dpi=200,
            layout="constrained"
        )

        kwargs_scatter = dict(
            s=16,
            alpha=0.8,
            edgecolors="black",
            linewidth=0.5
        )

        # Top-Left: Concentrations
        ax[0, 0].scatter(
            time_vals,
            c_glucose,
            label="Glucose",
            color="tab:blue",
            marker="o",
            **kwargs_scatter
        )

        ax[0, 0].scatter(
            time_vals,
            c_biomass,
            label="Biomass",
            color="tab:orange",
            marker="^",
            **kwargs_scatter
        )

        ax[0, 0].scatter(
            time_vals,
            c_product,
            label="Product",
            color="tab:green",
            marker="s",
            **kwargs_scatter
        )

        ax[0, 0].set_ylabel("Concentration, C (g/L)")

        # Top-Right: Temperature compliance
        ax[0, 1].scatter(
            time_vals[temp_mask],
            temp_vals[temp_mask],
            label="Optimal",
            color="tab:green",
            marker="o",
            **kwargs_scatter
        )

        ax[0, 1].scatter(
            time_vals[~temp_mask],
            temp_vals[~temp_mask],
            label="Sub-Optimal",
            color="tab:red",
            marker="X",
            **kwargs_scatter
        )

        ax[0, 1].set_ylabel("Temperature, T (°C)")

        # Bottom-Left: pH compliance
        ax[1, 0].scatter(
            time_vals[ph_mask],
            ph_vals[ph_mask],
            label="Optimal",
            color="tab:green",
            marker="o",
            **kwargs_scatter
        )

        ax[1, 0].scatter(
            time_vals[~ph_mask],
            ph_vals[~ph_mask],
            label="Sub-Optimal",
            color="tab:red",
            marker="X",
            **kwargs_scatter
        )

        ax[1, 0].set_ylabel("pH (-)")

        # Bottom-Right: Dissolved Oxygen
        ax[1, 1].scatter(
            time_vals,
            do_vals,
            color="tab:blue",
            marker="o",
            **kwargs_scatter
        )

        ax[1, 1].set_ylabel("Dissolved Oxygen, DO (%)")

        # Format axes tick spacing, labels, and legends
        for axis in ax.flat:
            axis.xaxis.set_major_locator(MultipleLocator(6))
            axis.set_xlabel("Time, t (h)")

            if axis.get_legend_handles_labels()[1]:
                axis.legend(
                    labelspacing=0.15,
                    handlelength=0.75,
                    handletextpad=0.4,
                    borderpad=0.3,
                    loc="upper right"
                )

        # Save figure and close to release memory
        directory = os.path.dirname(filepath)

        if directory:
            os.makedirs(directory, exist_ok=True)

        fig.savefig(filepath)
        plt.close(fig)

    def export_summary(self, filepath):
        """
        Generates a batch summary table and exports it to a CSV file.

        Parameters
        ----------
        filepath : str
            Output CSV table path.

        Summary Table Columns
        ---------------------
        batch_id
            Batch identifier.

        ph_optimal_percent
            Percentage of measurements in a batch within the
            acceptable pH range, rounded to 2 decimal places.

        temperature_optimal_percent
            Percentage of measurements in a batch within the
            acceptable temperature range, rounded to 2 decimal places.

        C_product_g_L^-1_final
            Final product concentration for the batch.
        """

        unique_batch_ids = np.unique(self.df.loc[:, "batch_id"])
        records = []

        for b_id in unique_batch_ids:
            df_batch = self.extract_batch(b_id)

            ph_mask = self.optimal_ph_mask(df_batch)
            temp_mask = self.optimal_temperature_mask(df_batch)

            # Calculate compliance percentages rounded to 2 decimal places
            ph_opt_percent = np.round(np.mean(ph_mask) * 100, 2)
            temp_opt_percent = np.round(np.mean(temp_mask) * 100, 2)

            # Extract final product concentration
            c_product_final = df_batch.loc[:, "C_product_g_L^-1"].iloc[-1]

            record = {
                "batch_id": b_id,
                "ph_optimal_percent": ph_opt_percent,
                "temperature_optimal_percent": temp_opt_percent,
                "C_product_g_L^-1_final": c_product_final,
            }

            records.append(record)

        df_summary = pd.DataFrame(records)

        # Save summary table and create directory if necessary
        directory = os.path.dirname(filepath)

        if directory:
            os.makedirs(directory, exist_ok=True)

        df_summary.to_csv(filepath, index=False)