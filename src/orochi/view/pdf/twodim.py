import numpy as np
import matplotlib.pyplot as plt

def make_2d_plot(x: np.ndarray, y: np.ndarray, z: np.ndarray,
                 xlabel: str = r"$r$ / $\mathrm{\AA}$", ylabel: str = "time / min",
                 xlim=None, ylim=None, figsize=(8, 6)):
    """
    Creates a 2D image plot with color representing the 'y' data (Gr).

    Args:
        x (np.ndarray): Data for the x-axis ($r$).
        y (np.ndarray): Data for the color ($G(r)$).
        z (np.ndarray): Data for the y-axis (time).
        xlabel (str): Label for the x-axis. Defaults to "$r$ / $\mathrm{\AA}$".
        ylabel (str): Label for the y-axis. Defaults to "time / min".
        xlim (tuple, optional): Display range for the x-axis (min, max). If None, it's auto-set.
        ylim (tuple, optional): Display range for the y-axis (min, max). If None, it's auto-set.
        figsize (tuple, optional): Figure size for the plot. Defaults to (8, 6).
    """
    plt.figure(figsize=figsize) 

    mesh = plt.pcolormesh(x, z, y, shading='auto', cmap='viridis')
    plt.colorbar(mesh, label=r"$G(r)$ / $\mathrm{\AA}^{-2}$")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    if xlim is not None:
        plt.xlim(xlim)
    if ylim is not None:
        plt.ylim(ylim)

    plt.tight_layout()

def make_1d_plot(x: np.ndarray, y: np.ndarray, z: np.ndarray,
                 xlabel: str = r"$r$ / $\mathrm{\AA}$", ylabel: str = r"$G(r)$ / $\mathrm{\AA}^{-2}$", 
                 xlim=None, ylim=None, figsize=(8, 6), legend=False, line_color=None, face_color=None):
    """
    Creates multiple 1D line plots, coloring each line based on its corresponding 'z' value.

    Args:
        x (np.ndarray): Data for the x-axis ($r$).
        y (np.ndarray): Data for the y-axis ($G(r)$).
        z (np.ndarray): Values corresponding to each line (e.g., time). These values determine the color.
        xlabel (str): Label for the x-axis. Defaults to "$r$".
        ylabel (str): Label for the y-axis. Defaults to "$G(r)$".
        xlim (tuple, optional): Display range for the x-axis (min, max). If None, it's auto-set.
        ylim (tuple, optional): Display range for the y-axis (min, max). If None, it's auto-set.
        figsize (tuple, optional): Figure size for the plot. Defaults to (8, 6).
    """
    fig, ax = plt.subplots(figsize=figsize)

    if face_color is not None:
        # fig.set_facecolor(face_color)
        # ax = fig.add_subplot(111) 
        ax.set_facecolor(face_color)

    if line_color is None:
        cmap = plt.get_cmap("coolwarm")
        line_colors = []
        for i in range(np.size(z)):
            color_value = i / (np.size(z) - 1)
            line_colors.append(cmap(color_value))
    else:
        line_colors = line_color

    for i in range(np.size(z)):
        plt.plot(x[i], y[i], label=z[i], color=line_colors[i])

    if xlim is not None:
        plt.xlim(xlim)
    if ylim is not None:
        plt.ylim(ylim)

    if legend:
        plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0.,frameon=False)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()

  