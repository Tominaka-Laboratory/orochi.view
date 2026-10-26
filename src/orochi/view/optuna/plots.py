import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.interpolate import griddata
from itertools import combinations
import optuna
import optuna.importance
from optuna.importance import FanovaImportanceEvaluator 

# Set matplotlib parameters for publication-quality figures
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.titlesize'] = 16
plt.rcParams['grid.alpha'] = 0.7
plt.rcParams['grid.linestyle'] = '--'


def load_optuna_study(db_path: str, study_name: str) -> optuna.Study | None:
    """
    Loads an Optuna Study object from an SQLite DB file.

    Args:
        db_path (str): Path to the SQLite DB file.
        study_name (str): Name of the study to load.

    Returns:
        optuna.Study: The loaded Study object, or None if an error occurs.
    """
    try:
        study = optuna.load_study(study_name=study_name, storage=f"sqlite:///{db_path}")
        print(f"Study '{study_name}' successfully loaded from '{db_path}'.")
        return study
    except Exception as e:
        print(f"Error loading study: {e}")
        return None


def plot_objective_convergence(df: pd.DataFrame, metric_col: str = 'value', title: str = "Objective Value Convergence", figsize: tuple = (8, 5), use_log_scale: bool = True, x_axis_type: str = 'trial_number') -> plt.Figure:
    """
    Plots the convergence curve of the objective function.
    The x-axis can be set to 'trial_number' or 'elapsed_time'.

    Args:
        df (pd.DataFrame): DataFrame containing Optuna trial data.
        metric_col (str): Name of the column containing the objective values (typically 'value').
        title (str): Title of the plot.
        figsize (tuple): Figure size (width, height) in inches.
        use_log_scale (bool): Whether to use a logarithmic scale for the y-axis.
        x_axis_type (str): Type of x-axis to plot. Can be 'trial_number' or 'elapsed_time'.

    Returns:
        plt.Figure: The generated matplotlib Figure object.
    """
    fig = plt.figure(figsize=figsize)

    if x_axis_type == 'elapsed_time':
        if 'datetime_start' not in df.columns or 'datetime_complete' not in df.columns:
            print("Warning: 'datetime_start' or 'datetime_complete' columns not found for elapsed time plotting. Falling back to 'trial_number'.")
            x_axis_type = 'trial_number'
        else:
            df['datetime_start'] = pd.to_datetime(df['datetime_start'])
            df['datetime_complete'] = pd.to_datetime(df['datetime_complete'])
            
            start_time_of_study = df['datetime_start'].min()
            
            df['elapsed_time'] = (df['datetime_complete'] - start_time_of_study).dt.total_seconds()
            
            df_sorted = df.sort_values(by='elapsed_time')
            x_values = df_sorted['elapsed_time']
            x_label = "Elapsed time (seconds)"
    else:
        df_sorted = df.sort_values(by="number")
        x_values = df_sorted["number"]
        x_label = "Trial number"

    plt.plot(x_values, df_sorted[metric_col].cummin(), label='Cumulative minimum', color='red', linewidth=2)
    plt.scatter(x_values, df_sorted[metric_col], alpha=0.6, s=10, label='Trial value', color='blue')
    
    plt.xlabel(x_label, fontsize=12)
    plt.ylabel("Objective value", fontsize=12)
    
    if use_log_scale:
        plt.yscale('log')
        plt.ylabel("Objective value (log scale)", fontsize=12)

    plt.title(title, fontsize=14)
    plt.grid(True)
    plt.legend(fontsize=10)
    plt.tight_layout()
    
    return fig

def plot_parameter_importance(study: optuna.Study, title: str = "Parameter Importance", figsize: tuple = (6, 5)) -> plt.Figure | None:
    """
    Plots the importance of hyperparameters.

    Args:
        study (optuna.Study): The Optuna Study object.
        title (str): Title of the plot.
        figsize (tuple): Figure size (width, height) in inches.

    Returns:
        plt.Figure: The generated matplotlib Figure object, or None if no importances to plot.
    """
    try:
        importances = optuna.importance.get_param_importances(
            study=study,
            evaluator=FanovaImportanceEvaluator()
        )
        if not importances:
            print("No parameter importances to plot. Ensure trials are completed.")
            return None

        param_names = list(importances.keys())
        importance_values = list(importances.values())

        sorted_indices = np.argsort(importance_values)[::-1]
        param_names_sorted = [param_names[i] for i in sorted_indices]

        cleaned_param_names = []
        for name in param_names_sorted:
            display_param_name = name.replace('params_', '')
            display_param_name_parts = display_param_name.split("/")
            display_param_name_filtered = [p for p in display_param_name_parts if p != "value"]
            cleaned_param_names.append("_".join(display_param_name_filtered))
        
        importance_values_sorted = [importance_values[i] for i in sorted_indices]

        fig = plt.figure(figsize=figsize)
        sns.barplot(x=importance_values_sorted, y=cleaned_param_names, palette='viridis')
        plt.xlabel("Importance", fontsize=12)
        plt.ylabel("Hyperparameter", fontsize=12)
        plt.title(title, fontsize=14)
        plt.grid(axis='x')
        plt.tight_layout()
        
        return fig

    except Exception as e:
        print(f"Error calculating or plotting parameter importance: {e}")
        return None


def plot_parameter_vs_objective(df: pd.DataFrame, param_cols: list[str], objective_col: str = 'value', title_prefix: str = "Parameter vs. Objective for", figsize_multiplier: tuple = (5, 4)) -> plt.Figure | None:
    """
    Plots the relationship between each hyperparameter and the objective function.

    Args:
        df (pd.DataFrame): DataFrame containing Optuna trial data.
        param_cols (list): List of hyperparameter column names to plot (e.g., ['params_x', 'params_y']).
        objective_col (str): Name of the column containing the objective values.
        title_prefix (str): Prefix for the plot titles.
        figsize_multiplier (tuple): Multipliers for width and height of each subplot.

    Returns:
        plt.Figure: The generated matplotlib Figure object, or None if no parameters to plot.
    """
    num_params = len(param_cols)
    if num_params == 0:
        print("No parameters specified for plotting.")
        return None

    cols_per_row = 3
    rows = int(np.ceil(num_params / cols_per_row))

    fig = plt.figure(figsize=(cols_per_row * figsize_multiplier[0], rows * figsize_multiplier[1]))

    for i, param in enumerate(param_cols):
        plt.subplot(rows, cols_per_row, i + 1)
        
        cleaned_param_name = "_".join([p for p in param.replace('params_', '').split('/') if p != "value"])

        if df[param].dtype in ['float64', 'int64'] and len(df[param].unique()) > 10:
            sns.scatterplot(x=df[param], y=df[objective_col], alpha=0.6)
            plt.xlabel(cleaned_param_name, fontsize=10)
        else:
            sns.boxplot(x=df[param], y=df[objective_col])
            plt.xlabel(cleaned_param_name, fontsize=10)
        
        plt.ylabel("Objective Value", fontsize=10)
        plt.grid(True)
    plt.tight_layout()
    
    return fig

def plot_parameter_correlations(df: pd.DataFrame, param_cols: list[str], title: str = "Hyperparameter Correlation Matrix", figsize: tuple = (8, 7)) -> plt.Figure | None:
    """
    Plots the correlation matrix between continuous hyperparameters.

    Args:
        df (pd.DataFrame): DataFrame containing Optuna trial data.
        param_cols (list): List of hyperparameter column names (e.g., ['params_x', 'params_y']).
        title (str): Title of the plot.
        figsize (tuple): Figure size (width, height) in inches.

    Returns:
        plt.Figure: The generated matplotlib Figure object, or None if no continuous parameters to plot.
    """
    numerical_params = [col for col in param_cols if df[col].dtype in ['float64', 'int64']]
    
    if not numerical_params:
        print("No numerical parameters found for correlation plotting.")
        return None

    cleaned_numerical_params = []
    for param in numerical_params:
        display_param_name = param.replace('params_', '')
        display_param_name_parts = display_param_name.split("/")
        display_param_name_filtered = [p for p in display_param_name_parts if p != "value"]
        cleaned_numerical_params.append("_".join(display_param_name_filtered))
    
    df_params = df[numerical_params].copy()
    df_params.columns = cleaned_numerical_params

    corr_matrix = df_params.corr(method='pearson')

    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5, ax=ax)
    ax.set_title(title, fontsize=14)
    plt.tight_layout()
    return fig

def plot_parameter_distributions(df: pd.DataFrame, param_cols: list[str], title_prefix: str = "Distribution of", figsize_multiplier: tuple = (4, 3)) -> plt.Figure | None:
    """
    Plots the distribution of explored hyperparameters (histograms for numerical, count plots for categorical).

    Args:
        df (pd.DataFrame): DataFrame containing Optuna trial data.
        param_cols (list): List of hyperparameter column names.
        title_prefix (str): Prefix for subplot titles.
        figsize_multiplier (tuple): Multipliers for width and height of each subplot.

    Returns:
        plt.Figure: The generated matplotlib Figure object, or None if no parameters to plot.
    """
    if not param_cols:
        print("No parameters specified for distribution plotting.")
        return None

    num_params = len(param_cols)
    cols_per_row = 3
    rows = int(np.ceil(num_params / cols_per_row))

    fig = plt.figure(figsize=(cols_per_row * figsize_multiplier[0], rows * figsize_multiplier[1]))

    for i, param in enumerate(param_cols):
        ax = fig.add_subplot(rows, cols_per_row, i + 1)
        
        cleaned_param_name = "_".join([p for p in param.replace('params_', '').split('/') if p != "value"])

        if df[param].dtype in ['float64', 'int64'] and len(df[param].unique()) > 10:
            sns.histplot(df[param], kde=True, ax=ax, color='skyblue')
            ax.set_xlabel(cleaned_param_name, fontsize=10)
            ax.set_ylabel("Count", fontsize=10)
        else:
            sns.countplot(x=df[param], ax=ax, palette='viridis')
            ax.set_xlabel(cleaned_param_name, fontsize=10)
            ax.set_ylabel("Count", fontsize=10)
            ax.tick_params(axis='x', rotation=45, ha='right')

        ax.set_title(f"{title_prefix} {cleaned_param_name}", fontsize=12)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    return fig

def plot_contour_map(df: pd.DataFrame, param1: str, param2: str, objective_col: str = 'value', title: str = "Contour Plot", figsize: tuple = (8, 6), num_grid_points: int = 100) -> plt.Figure | None:
    """
    Plots a 2D contour map of the objective function over two parameters.

    Args:
        df (pd.DataFrame): DataFrame containing Optuna trial data.
        param1 (str): Name of the first parameter column (e.g., 'params_x'). Must be numerical.
        param2 (str): Name of the second parameter column (e.g., 'params_y'). Must be numerical.
        objective_col (str): Name of the objective value column.
        title (str): Title of the plot.
        figsize (tuple): Figure size (width, height) in inches.
        num_grid_points (int): Number of points for the grid along each axis for interpolation.

    Returns:
        plt.Figure: The generated matplotlib Figure object, or None if parameters are not numerical or data is insufficient.
    """
    df_plot = df.dropna(subset=[param1, param2, objective_col])

    if not df_plot[param1].dtype in ['float64', 'int64'] or not df_plot[param2].dtype in ['float64', 'int64']:
        print(f"Error: Parameters '{param1}' and '{param2}' must be numerical for contour plot.")
        return None
    
    if len(df_plot) < 4:
        print(f"Not enough data points ({len(df_plot)} < 4) to create a contour plot for '{param1}' and '{param2}'.")
        return None

    x = df_plot[param1].values
    y = df_plot[param2].values
    z = df_plot[objective_col].values

    xi = np.linspace(x.min(), x.max(), num_grid_points)
    yi = np.linspace(y.min(), y.max(), num_grid_points)
    
    zi = griddata((x, y), z, (xi[None, :], yi[:, None]), method='cubic')

    fig, ax = plt.subplots(figsize=figsize)

    contour_plot = ax.contourf(xi, yi, zi, levels=20, cmap='viridis_r', alpha=0.8)
    plt.colorbar(contour_plot, label="Objective Value")
    
    ax.scatter(x, y, c='black', s=10, alpha=0.6, label='Explored trials')
    
    display_param1 = "_".join([p for p in param1.replace('params_', '').split('/') if p != 'value'])
    display_param2 = "_".join([p for p in param2.replace('params_', '').split('/') if p != 'value'])

    ax.set_xlabel(display_param1, fontsize=12)
    ax.set_ylabel(display_param2, fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend(fontsize=10)
    plt.tight_layout()
    
    return fig

def plot_all_contour_maps(df: pd.DataFrame, param_cols: list[str], objective_col: str = 'value', title_prefix: str = "Contour Plot", figsize_multiplier: tuple = (6, 5), num_grid_points: int = 100) -> list[plt.Figure]:
    """
    Plots contour maps for all unique pairs of continuous hyperparameters.

    Args:
        df (pd.DataFrame): DataFrame containing Optuna trial data.
        param_cols (list): List of hyperparameter column names.
        objective_col (str): Name of the objective value column.
        title_prefix (str): Prefix for subplot titles.
        figsize_multiplier (tuple): Multipliers for width and height of each subplot.
        num_grid_points (int): Number of points for the grid along each axis for interpolation.

    Returns:
        list[plt.Figure]: A list of generated matplotlib Figure objects.
    """
    figs = []
    numerical_param_cols = [col for col in param_cols if df[col].dtype in ['float64', 'int64']]

    if len(numerical_param_cols) < 2:
        print("Not enough numerical parameters (at least 2) to create contour plots.")
        return figs

    param_pairs = list(combinations(numerical_param_cols, 2))

    for param1, param2 in param_pairs:
        display_name_p1 = "_".join([p for p in param1.replace('params_', '').split('/') if p != 'value'])
        display_name_p2 = "_".join([p for p in param2.replace('params_', '').split('/') if p != 'value'])
        
        fig = plot_contour_map(df, param1, param2, objective_col, 
                               title=f"{title_prefix}: {display_name_p1} vs {display_name_p2}",
                               figsize=figsize_multiplier, num_grid_points=num_grid_points)
        if fig:
            figs.append(fig)
    
    return figs


def plot_all_contour_maps_in_one_fig(df: pd.DataFrame, param_cols: list[str], objective_col: str = 'value', main_title: str = "Contour Plots of Parameter Pairs", figsize_multiplier: tuple = (6, 5), num_grid_points: int = 100) -> plt.Figure | None:
    """
    Plots contour maps for all unique pairs of continuous hyperparameters in a single figure with subplots.

    Args:
        df (pd.DataFrame): DataFrame containing Optuna trial data.
        param_cols (list): List of hyperparameter column names.
        objective_col (str): Name of the objective value column.
        main_title (str): Overall title for the entire figure.
        figsize_multiplier (tuple): Multipliers for width and height of each subplot.
        num_grid_points (int): Number of points for the grid along each axis for interpolation.

    Returns:
        plt.Figure: The generated matplotlib Figure object, or None if no numerical parameters or pairs.
    """
    numerical_param_cols = [col for col in param_cols if df[col].dtype in ['float64', 'int64']]

    if len(numerical_param_cols) < 2:
        print("Not enough numerical parameters (at least 2) to create contour plots.")
        return None

    param_pairs = list(combinations(numerical_param_cols, 2))
    num_pairs = len(param_pairs)

    if num_pairs == 0:
        print("No valid parameter pairs found for contour plots.")
        return None

    cols_per_row = min(3, num_pairs)
    rows = int(np.ceil(num_pairs / cols_per_row))

    fig, axes = plt.subplots(rows, cols_per_row, figsize=(cols_per_row * figsize_multiplier[0], rows * figsize_multiplier[1]), squeeze=False)
    axes = axes.flatten()

    for i, (param1, param2) in enumerate(param_pairs):
        ax = axes[i]
        
        df_plot = df.dropna(subset=[param1, param2, objective_col])

        if len(df_plot) < 4:
            print(f"Skipping contour plot for '{param1}' vs '{param2}': Insufficient data points ({len(df_plot)} < 4).")
            ax.set_visible(False)
            continue

        x = df_plot[param1].values
        y = df_plot[param2].values
        z = df_plot[objective_col].values

        xi = np.linspace(x.min(), x.max(), num_grid_points)
        yi = np.linspace(y.min(), y.max(), num_grid_points)
        
        zi = griddata((x, y), z, (xi[None, :], yi[:, None]), method='linear')

        contour_plot = ax.contourf(xi, yi, zi, levels=20, cmap='viridis_r', alpha=0.8)
        fig.colorbar(contour_plot, ax=ax, label="Objective Value")
        
        ax.scatter(x, y, c='black', s=10, alpha=0.6, label='Explored trials')
        
        display_param1 = "_".join([p for p in param1.replace('params_', '').split('/') if p != 'value'])
        display_param2 = "_".join([p for p in param2.replace('params_', '').split('/') if p != 'value'])

        ax.set_xlabel(display_param1, fontsize=10)
        ax.set_ylabel(display_param2, fontsize=10)
        ax.grid(True)
    
    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    fig.suptitle(main_title, fontsize=16, y=1.02)
    plt.tight_layout(rect=[0, 0, 1, 0.98])
    
    return fig