from typing import Callable

import pandas as pd
import plotly.graph_objects as go

def create_2d_cartesian_plot_as_subplot(
    subplots_fig: go.Figure,
    plot_func: Callable[..., go.Figure],
    df: pd.DataFrame,
    subplot_row,
    subplot_col,
    x_label=None,
    y_label=None,
    **plot_func_kwargs
):
    """Create a 2D Cartesian plot as a subplot.
    
    Parameters
    ----------
    subplots_fig : go.Figure
        The subplot figure to create the plot in.
    plot_func : Callable[..., go.Figure]
        A function for 2D Cartesian plots.
    df : pd.DataFrame
        DataFrame with the data to plot.
    subplot_row : int
        Row index of the subplot (1-based).
    subplot_col : int
        Column index of the subplot (1-based).
    x_label : str, optional
        Label for the x-axis.
    y_label : str, optional
        Label for the y-axis.
    **plot_func_kwargs
        Additional arguments passed to `plot_func`. If `orientation='h'`,
        then the x- and y-axis data, and the x_label and y_label values, are swapped.
    """

    # Swap x- and y-axis data, and the x_label and y_label values, if horizontal orientation is set.
    if plot_func_kwargs.get('orientation') == 'h':
        plot_func_kwargs['x'], plot_func_kwargs['y'] = plot_func_kwargs.get('y'), plot_func_kwargs.get('x')
        x_label, y_label = y_label, x_label

    # Build the Plotly Express figure and copy its traces to the subplot.
    temp_fig = plot_func(df, **plot_func_kwargs)
    for trace in temp_fig.data:
        subplots_fig.add_trace(trace, row=subplot_row, col=subplot_col)

    # Apply axis labels if provided.
    if x_label is not None:
        subplots_fig.update_xaxes(title_text=x_label, row=subplot_row, col=subplot_col)
    if y_label is not None:
        subplots_fig.update_yaxes(title_text=y_label, row=subplot_row, col=subplot_col)