import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.ticker import FormatStrFormatter

def plot(df, 
        xlabel: str = r"$r$ / $\mathrm{\AA}$", 
        ylabel: str = r"$g(r)$ / $\mathrm{\AA}^{-2}$", 
        figsize=(8, 6), 
        legend=False, 
        face_color=None, 
        secondy="OO",
        **kwargs):
    """
    Creates multiple 1D line plots, coloring each line based on its corresponding 'z' value.

    Args:
        df: dataframe 
        xlabel (str): Label for the x-axis. Defaults to "$r$".
        ylabel (str): Label for the y-axis. Defaults to "$G(r)$".
        figsize (tuple, optional): Figure size for the plot. Defaults to (8, 6).
    """

    fig, ax = plt.subplots(figsize=figsize, dpi=200)
    if secondy is not None:
        ax2 = ax.twinx()

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

    majForm4 = FormatStrFormatter("%1.0f")
    ax.xaxis.set_major_formatter(majForm4)
    # Custom format for coordinate display on hover
    ax.format_coord = lambda x, y: "%.3f, %.3f" % (x, y)

    # Set major formatter for y-axis (though not explicitly used for major ticks, good practice)
    majForm4 = FormatStrFormatter("%1.0f")
    ax.yaxis.set_major_formatter(majForm4)
    # Set minor locator for x-axis
    ax.xaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator(5))

    r = df["r"]
    df_y = df.drop(columns=["r"])
    lines = []

    for name, data in df_y.items():
        if name == "OO":
            color = "red"
            name = "O-O"
            axis = ax2
            ax2.set_ylim(None, data.max() * 2)
        elif "O" in name:
            color = "blue"
            name = "M-O"
            axis = ax
        else:
            color = "black"
            name = "M-M"
            axis = ax
        line, = axis.plot(r, data, label=name, color=color)
        lines.append(line)

    if legend:
        fig.legend(handles=lines, bbox_to_anchor=(0.85, 0.93), loc='upper right', borderaxespad=0.2, frameon=False)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    if secondy is not None:
        ax2.set_ylabel(ylabel+" (O-O)")

    xmin = None
    xmax = None
    if "xmin" in kwargs:
        xmin = kwargs["xmin"]
    if "xmax" in kwargs:
        xmax = kwargs["xmax"]

    if "xmin" in kwargs or "xmax" in kwargs:
        ax.set_xlim(xmin, xmax)

    plt.tight_layout()

    return fig, ax





  