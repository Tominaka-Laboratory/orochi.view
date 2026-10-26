import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.ticker import FormatStrFormatter

def plot(obsx: np.ndarray, 
                 obsy: np.ndarray, 
                 simx: np.ndarray, 
                 simy: np.ndarray, 
                 xlabel: str = r"$r$ / $\mathrm{\AA}$", 
                 ylabel: str = r"$G(r)$ / $\mathrm{\AA}^{-2}$", 
                 figsize=(8, 6), legend=False, face_color=None, **kwargs):
    """
    Creates multiple 1D line plots, coloring each line based on its corresponding 'z' value.

    Args:
        x (np.ndarray): Data for the x-axis ($r$).
        y (np.ndarray): Data for the y-axis ($G(r)$).
        xlabel (str): Label for the x-axis. Defaults to "$r$".
        ylabel (str): Label for the y-axis. Defaults to "$G(r)$".
        figsize (tuple, optional): Figure size for the plot. Defaults to (8, 6).
    """
    if "number" in kwargs:
        number = kwargs["number"]
    else:
        number = None

    fig, ax = plt.subplots(num=number, figsize=figsize, dpi=400)

    if face_color is not None:
        ax.set_facecolor(face_color)
    if "fontsize" in kwargs:
        plt.rcParams["font.size"] = kwargs["fontsize"]
        labelfont = kwargs["fontsize"]
    else:
        plt.rcParams["font.size"] = 14
        labelfont = 14

    plt.rcParams["axes.linewidth"] = 1.0
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Liberation Sans']

    majForm4 = FormatStrFormatter("%1.1f")
    ax.xaxis.set_major_formatter(majForm4)
    # Custom format for coordinate display on hover
    ax.format_coord = lambda x, y: "%.3f, %.3f" % (x, y)

    # Set major formatter for y-axis (though not explicitly used for major ticks, good practice)
    majForm4 = FormatStrFormatter("%1.0f")
    ax.yaxis.set_major_formatter(majForm4)
    # Set minor locator for x-axis
    ax.xaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator(5))

    ax.plot(obsx, obsy, label="obs", color="blue", ls="", marker="o", mfc=None, mec="blue", mew=0.2, markersize=4.0)
    ax.plot(simx, simy, label="sim", color="red", ls="-", lw=2)

    diff = obsy - np.interp(obsx, simx, simy)
    diff = diff + np.amin(obsy) * 1.1 - np.amax(diff)
    ax.plot(obsx, diff, label="diff.", color="green", lw=2)

    xmin = None
    xmax = None
    if "xmin" in kwargs:
        xmin = kwargs["xmin"]
    if "xmax" in kwargs:
        xmax = kwargs["xmax"]

    if "xmin" in kwargs or "xmax" in kwargs:
        ax.set_xlim(xmin, xmax)

    if legend:
        plt.legend(bbox_to_anchor=(0.85, 0.93), loc='upper right', borderaxespad=0.2, frameon=False)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()

    # plt.show()

    return fig, ax





  