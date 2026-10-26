import matplotlib
matplotlib.use('QT5Agg')
matplotlib.interactive(True)
from matplotlib import pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import numpy as np

class Figure:
    """
    A class to create and manage Matplotlib figures for PDF (Pair Distribution Function)
    data visualization, including observed, simulated, and difference curves.

    The class sets up common plotting parameters like font sizes, line widths, and
    axis labels suitable for PDF plots. It also provides methods to set and update
    observed, simulated, and difference data, calculate R_w factor, and save the figure.
    """
    def __init__(self, number=1, **kwargs):
        """
        Initializes a new Figure object.

        Parameters
        ----------
        number : int, optional
            The figure number. If a figure with this number already exists,
            it will be cleared. Defaults to 1.
        **kwargs
            fontsize : int, optional
                Sets the global font size for the plot. Defaults to 14.
            figsize : tuple, optional
                Sets the figure size (width, height) in inches. Defaults to (7, 5).
            title : str, optional
                Sets the title of the plot.
        """
        if plt.fignum_exists(number):
            # plt.close(number) # Option to close and recreate the figure
            plt.clf() # Clear the current figure if it exists

        if "fontsize" in kwargs:
            plt.rcParams["font.size"] = kwargs["fontsize"]
            self.labelfont = kwargs["fontsize"]
        else:
            plt.rcParams["font.size"] = 14
            self.labelfont = 14

        plt.rcParams["axes.linewidth"] = 1.0
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Liberation Sans']

        if "figsize" in kwargs:
            figsize = kwargs["figsize"]
        else:
            figsize = (7, 5)

        self.fig, self.ax = plt.subplots(num=number, figsize=figsize, dpi=100)

        plt.xlabel(r"$r$ / $\mathrm{\AA}$", fontsize=self.labelfont)
        plt.ylabel(r"$G$($r$) / $\mathrm{\AA}$$^{-2}$", fontsize=self.labelfont)

        if "title" in kwargs:
            self.ax.set_title(kwargs["title"], loc="center")

        # Set major formatter for x-axis to display integers
        majForm4 = FormatStrFormatter("%1.0f")
        self.ax.xaxis.set_major_formatter(majForm4)
        # Custom format for coordinate display on hover
        self.ax.format_coord = lambda x, y: "%.3f, %.3f" % (x, y)

        # Set major formatter for y-axis (though not explicitly used for major ticks, good practice)
        majForm4 = FormatStrFormatter("%1.0f")
        self.ax.yaxis.set_major_formatter(majForm4)
        # Set minor locator for x-axis
        self.ax.xaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator(5))

        self.number = number
        self.shown = False

        # Draw the canvas and copy the background for blitting optimization
        self.fig.canvas.draw()
        self.bb = self.fig.canvas.copy_from_bbox(self.ax.bbox)

        # Initialize data lists
        self.obsx = []
        self.obsy = []
        self.simx = []
        self.simy = []
        self.diff = []

    def set_obs(self, datax, datay, label="obs"):
        """
        Sets or updates the observed PDF data on the plot.

        Parameters
        ----------
        datax : array_like
            X-coordinates (r values) of the observed PDF data.
        datay : array_like
            Y-coordinates (G(r) values) of the observed PDF data.
        """
        self.obsx = datax
        self.obsy = datay
        if "pobs" not in dir(self): # If plot object doesn't exist, create it
            (self.pobs,) = self.ax.plot(
                self.obsx,
                self.obsy,
                label=label,
                color="blue",
                ls="", # No line
                marker="o", # Circle markers
                mfc=None, # No marker face color (transparent)
                mec="blue", # Marker edge color
                mew=0.2, # Marker edge width
                # lw=2.0, # Line width (for the line if ls were not empty)
                markersize=4.0,
            )
        else: # Otherwise, just update the data
            self.pobs.set_data(self.obsx, self.obsy)

    def set_diff(self):
        """
        Calculates and sets the difference curve (observed - simulated PDF).
        The difference curve is shifted vertically for better visualization.
        """
        if self.obsx.tolist() == self.simx.tolist(): # Check if x-ranges are identical
            diff = self.obsy - self.simy
        else: # Interpolate simulated data onto observed x-points if ranges differ
            diff = self.obsy - np.interp(self.obsx, self.simx, self.simy)
        
        # Shift the difference curve for visualization
        # It's shifted to be below the main PDF curves, typically near the minimum of the observed PDF.
        if np.size(self.obsy) > 0 and np.size(diff) > 0:
            self.diff = diff + np.amin(self.obsy) * 1.1 - np.amax(diff)
        else:
            self.diff = diff # Handle empty case or adjust as needed

        if "pdiff" not in dir(self): # Create plot object if it doesn't exist
            (self.pdiff,) = self.ax.plot(
                self.obsx, self.diff, label="diff.", color="green", lw=2
            )
        else: # Update existing plot object
            self.pdiff.set_data(self.obsx, self.diff)

    def set_sim(self, datax, datay, label="sim"):
        """
        Sets or updates the simulated PDF data on the plot.

        Parameters
        ----------
        datax : array_like
            X-coordinates (r values) of the simulated PDF data.
        datay : array_like
            Y-coordinates (G(r) values) of the simulated PDF data.
        """
        self.simx = datax
        self.simy = datay
        self.ax.set_xlim(datax[0], datax[-1]) # Set x-axis limits based on sim data

        if "psimu" not in dir(self): # Create plot object if it doesn't exist
            (self.psimu,) = self.ax.plot(
                datax, datay, label=label, lw=2, color="red"
            )
        else: # Update existing plot object
            self.psimu.set_data(datax, datay)

    def calc_Rw(self):
        """
        Calculates and prints the weighted R-factor (Rw) between the observed
        and simulated PDF curves.
        """
        # Ensure obs and sim are numpy arrays for calculation
        obs_array = np.array(self.obsy)
        sim_array = np.array(self.simy)

        # Check if arrays are empty or have different lengths before calculation
        if obs_array.size == 0 or sim_array.size == 0 or obs_array.size != sim_array.size:
            print("Cannot calculate Rw: Observed or simulated data is missing or has inconsistent lengths.")
            self.rw = np.nan # Set to NaN if calculation is not possible
            return

        weight = 1.0 # Simple uniform weight; can be customized
        self.rw = np.sqrt(
            np.sum(weight * np.square(obs_array - sim_array))
            / np.sum(weight * np.square(obs_array))
        )

        print("Rw = " + "{:.4f}".format(self.rw) + "\n")

    def update(self):
        """
        Draws or updates the plot on the figure.

        If the figure is being shown for the first time, it sets axis limits,
        adjusts layout, and performs an initial blit. For subsequent draws,
        it uses blitting for faster updates of existing plot elements.

        Parameters
        ----------
        show_block : bool, optional
            If True, blocks execution and shows the plot. Useful for non-interactive
            environments or when you want to keep the plot window open. Defaults to False.
        """
        # Set x-axis limits based on available data
        if np.size(self.obsx) > 0:
            plt.xlim(np.floor(self.obsx[0]), np.ceil(self.obsx[-1]))
        elif np.size(self.simx) > 0: # Fallback if only simulation data is available
            plt.xlim(np.floor(self.simx[0]), np.ceil(self.simx[-1]))
        self.fig.tight_layout() # Adjust plot params for a tight layout
        self.ax.autoscale(enable=True, axis="y") # Autoscale y-axis
        
    def draw(self, show_block=False):
        if self.shown == False:
            self.shown = True
            # self.fig.show() # Can be used for initial display, but flush_events is often enough
            self.fig.canvas.blit(self.ax.bbox) # Initial blit of the axes
            self.fig.canvas.flush_events() # Process GUI events
        else:
            # Restore the background for faster updates
            self.fig.canvas.restore_region(self.bb)
            # Redraw only the artists that have changed
            if hasattr(self, 'psimu'): self.ax.draw_artist(self.psimu)
            if hasattr(self, 'pobs'): self.ax.draw_artist(self.pobs)
            if hasattr(self, 'pdiff'): self.ax.draw_artist(self.pdiff)

            self.ax.relim("y") # Recalculate y-limits
            self.ax.autoscale_view() # Autoscale y-axis view
            self.fig.tight_layout() # Readjust layout

            self.fig.canvas.blit(self.ax.bbox) # Blit updated axes
            self.fig.canvas.flush_events() # Process GUI events

        if show_block:
            plt.show(block=True)

    def save(self, filename, **kwargs):
        """
        Saves the current figure to a file.

        Parameters
        ----------
        filename : str
            The path and name of the file to save (e.g., "my_plot.png").
        **kwargs
            dpi : int, optional
                The resolution in dots per inch. Defaults to 200.
        """
        if "dpi" in kwargs:
            dpi = kwargs["dpi"]
        else:
            dpi = 200
        self.fig.savefig(filename, dpi=dpi)

    def close(self):
        """
        Closes the Matplotlib figure.
        """
        plt.close(self.number)