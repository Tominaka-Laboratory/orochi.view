import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot(obsx: np.ndarray = None,
         obsy: np.ndarray = None,
         simx: np.ndarray = None,
         simy: np.ndarray = None,
         xlabel: str = "r / \u212B", # X-axis label (using Unicode for Ångström)
         ylabel: str = "G(r) / \u212B\u207B\u00B2", # Y-axis label (using Unicode for Ångström and superscript -2)
         figsize=(None, 600), # Plot size (width, height) in pixels
         legend=False, # Whether to display the legend
         face_color: str = None, # Background color of the plot area (defaults to white if None)
         **kwargs):
    """
    Generates an interactive Plotly graph for observed, simulated, and difference data.

    This function creates a 1D line plot similar to matplotlib's default style,
    with options for displaying observed data as markers, simulated data as a line,
    and their difference. It configures axis formatting, background colors,
    and legend display.

    Parameters
    ----------
    obsx : np.ndarray, optional
        X-axis data for observed points.
    obsy : np.ndarray, optional
        Y-axis data for observed points. If None, observed data will not be plotted.
    simx : np.ndarray, optional
        X-axis data for simulated line.
    simy : np.ndarray, optional
        Y-axis data for simulated line. If None, simulated data and difference will not be plotted.
    xlabel : str, optional
        Label for the X-axis, can include Unicode characters.
        Defaults to "r / Å".
    ylabel : str, optional
        Label for the Y-axis, can include Unicode characters.
        Defaults to "G(r) / Å⁻²".
    figsize : tuple, optional
        Figure size in pixels (width, height). Defaults to (800, 600).
    legend : bool, optional
        If True, a legend will be displayed. Defaults to False.
    face_color : str, optional
        Background color of the plot area. If None, defaults to 'white'.
        E.g., '#F0F0F0', 'lightgray'.
    **kwargs
        Additional keyword arguments for general plot customization, e.g., 'fontsize'.

    Returns
    -------
    plotly.graph_objects.Figure
        The configured Plotly Figure object.

    Notes
    -----
    - For proper display of Ångström and superscript characters, Unicode is used
      instead of LaTeX given potential rendering issues in some environments.
    - The Plotly mode bar position (e.g., top-right) cannot be directly controlled
      to move it to the top or bottom using this Python API.
    """

    fig = make_subplots(
        rows=1,
        cols=1,
        horizontal_spacing=0., # Horizontal spacing between subplots
        vertical_spacing=0., # Vertical spacing between subplots
    )

    # 1. Observed Data (Scatter plot)
    if obsy is not None and obsx is not None:
        fig.add_trace(
            go.Scatter(
                x=obsx,
                y=obsy,
                mode='markers', # Display as markers
                marker=dict(
                    color="blue", # Set marker color to blue
                    size=4, # Marker size
                    line=dict(width=0.2, color='blue') # Marker outline color and width
                ),
                name="obs", # Entry name for the legend
                showlegend=True if legend else False # Show legend entry if legend is enabled
            ),
            row=1, col=1
        )

    # 2. Simulated Data (Line plot)
    if simy is not None and simx is not None:
        fig.add_trace(
            go.Scatter(
                x=simx,
                y=simy,
                mode='lines', # Display as lines
                line=dict(
                    color="red", # Set line color to red
                    width=2 # Line width
                ),
                name="sim", # Entry name for the legend
                showlegend=True if legend else False # Show legend entry if legend is enabled
            ),
            row=1, col=1
        )

    # 3. Difference (Difference plot)
    if (
        obsy is not None
        and simy is not None
        and obsx is not None
        and simx is not None
        and len(obsx) > 0
        and len(simx) > 0
    ):
        diff = obsy - np.interp(obsx, simx, simy)
        # Adjust difference plot offset to align with observed data's minimum
        diff_offset = np.amin(obsy) * 1.1 - np.amax(diff)
        diff = diff + diff_offset

        fig.add_trace(
            go.Scatter(
                x=obsx,
                y=diff,
                mode='lines', # Display as lines
                line=dict(
                    color="green", # Set line color to green
                    width=2 # Line width
                ),
                name="diff.", # Entry name for the legend
                showlegend=True if legend else False # Show legend entry if legend is enabled
            ),
            row=1, col=1
        )

    font_size = kwargs.get("fontsize", 14)
    
    # Determine plot background color (default to white if not specified)
    plot_bg_color = face_color if face_color is not None else 'white'

    # Update plot layout settings
    fig.update_layout(
        title_text="", # No main title for the plot
        xaxis_title=xlabel, # X-axis label
        yaxis_title=ylabel, # Y-axis label
        font=dict(
            size=font_size, # Set global font size
        ),
        width=figsize[0], # Figure width
        height=figsize[1], # Figure height
        plot_bgcolor=plot_bg_color, # Set background color of the plot area
        paper_bgcolor='white', # Set background color of the entire figure (outside plot area)
        hovermode="x unified" if legend else "closest", # Hover behavior for interactive plots
    )

    # --- Adjust margins for top and right ---
    # Default margins are usually around l=80, r=80, t=100, b=100
    # Setting them to specific values (e.g., 20) provides a balance
    # between compact layout and avoiding cutoff elements.
    fig.update_layout(
        margin=dict(
            l=80, # Left margin (default is usually sufficient for y-axis labels)
            r=80, # Right margin (reduced from default 80 to 0)
            t=0, # Top margin (reduced from default 100 to 0)
            b=80  # Bottom margin (default is usually sufficient for x-axis labels)
        )
    )

    # --- Set X-axis range based on data ---
    x_min_val = None
    x_max_val = None

    if obsx is not None and len(obsx) > 0:
        x_min_val = np.min(obsx)
        x_max_val = np.max(obsx)

    if simx is not None and len(simx) > 0:
        if x_min_val is None or np.min(simx) < x_min_val:
            x_min_val = np.min(simx)
        if x_max_val is None or np.max(simx) > x_max_val:
            x_max_val = np.max(simx)
    
    if x_min_val is not None and x_max_val is not None:
        fig.update_xaxes(range=[x_min_val, x_max_val])
    # --- End X-axis range setting ---

    # Update X-axis properties
    fig.update_xaxes(
        tickformat=".0f", # Format ticks as integers
        mirror=True, # Draw axis line on the opposite side
        showline=True, # Show axis line
        linewidth=1, # Axis line width
        linecolor='black', # Axis line color
        ticks='inside', # Show ticks inside the plot area
        showgrid=False, # Disable major grid lines
        title_standoff=10, # Distance between axis title and axis
        minor=dict(
            showgrid=False, # Disable minor grid lines
            tickmode='auto', # Automatically determine minor tick placement
            nticks=5, # Approximate number of minor ticks between major ticks
        )
    )
    # Update Y-axis properties
    fig.update_yaxes(
        tickformat=".0f", # Format ticks as integers
        mirror=True, # Draw axis line on the opposite side
        showline=True, # Show axis line
        linewidth=1, # Axis line width
        linecolor='black', # Axis line color
        ticks='inside', # Show ticks inside the plot area
        showgrid=False, # Disable major grid lines
        title_standoff=10, # Distance between axis title and axis
        minor=dict(
            showgrid=False, # Disable minor grid lines
            tickmode='auto', # Automatically determine minor tick placement
            nticks=5, # Approximate number of minor ticks between major ticks
        )
    )

    # Configure legend if enabled
    if legend:
        fig.update_layout(
            legend=dict(
                x=1.02, # X position of the legend (relative to plot area)
                y=1,    # Y position of the legend (relative to plot area)
                xanchor='left', # Anchor point of the legend (left side aligned to x)
                yanchor='top',  # Anchor point of the legend (top side aligned to y)
                bgcolor='rgba(255,255,255,0.7)', # Legend background color (semi-transparent white)
                bordercolor='rgba(0,0,0,0)', # Legend border color (transparent)
                borderwidth=0 # No legend border
            )
        )
    
    # Configure modebar (buttons like zoom, pan, reset)
    fig.update_layout(
        modebar={
            'orientation': 'v', # Vertical orientation for the modebar
            'bgcolor': 'rgba(0,0,0,0)', # Managed via Orochi CSS theme
            'color': '#475569', # Slate icon color
            'activecolor': '#0284c7', # Sapphire blue active color
        }
    )
    
    return fig
