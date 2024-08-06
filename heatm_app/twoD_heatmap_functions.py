import os
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from brainrender import Scene
import numpy as np
import pandas as pd
import easygui
from scipy.stats import gaussian_kde
from scipy.ndimage import gaussian_filter
import tkinter as tk


def create_transparent_bottomed_cmap(predefined_cmap_name):
    default_cmap = plt.get_cmap(predefined_cmap_name)
    ncolors = default_cmap.N

    # Create a gradient from transparent to the colors of the original colormap
    transparent_colors = np.zeros((ncolors, 4))
    transparent_colors[:, 0:3] = default_cmap(np.linspace(0, 1, ncolors))[:, 0:3]  # Get RGB values
    transparent_colors[:, 3] = np.linspace(0, 1, ncolors)  # Alpha from 0 (transparent) to 1 (opaque)

    # Create the final colormap
    return ListedColormap(transparent_colors)


"""def plot_shadowed_heatmap_and_histogram(lr_data, dv_data, lr_shadow, dv_shadow, lr_limits, dv_limits, save_dir=None, bin_edges=None):
    # Create Figure
    fig = plt.figure(figsize=(10, 8))
    gs = fig.add_gridspec(4, 4)
    ax_main = fig.add_subplot(gs[1:4, 0:3])

    # Shadow Histogram
    shadow_hist, xedges, yedges = np.histogram2d(
        lr_shadow,
        dv_shadow,
        bins=150,
        range=[[lr_limits[0], lr_limits[1]], [dv_limits[0], dv_limits[1]]]
    )
    shadow_hist = gaussian_filter(shadow_hist, sigma=1)
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    ax_main.imshow(np.rot90(shadow_hist), cmap="Greys", extent=extent, aspect='auto')

    # Data Heatmap
    try:
        xy_data = np.vstack([lr_data, dv_data])
        kde_data = gaussian_kde(xy_data)
        xmin, xmax = lr_limits
        ymin, ymax = dv_limits
        x, y = np.mgrid[xmin:xmax:100j, ymin:ymax:100j]
        positions_data = np.vstack([x.ravel(), y.ravel()])
        z = np.reshape(kde_data(positions_data).T, x.shape)
        custom_cmap = create_transparent_bottomed_cmap('plasma')
        ax_main.imshow(np.rot90(z), cmap=custom_cmap, extent=[xmin, xmax, ymin, ymax], aspect='auto')
    except ValueError as e:
        print("no data")
        # Skip heatmap part

    ax_main.axvline(x=5700, color="black", linestyle=":")

    # Set axis limits of 2D heatmap
    padx = 1000
    pady = 1000
    ax_main.set_xlim(lr_limits[0] - padx, lr_limits[1] + padx)
    ax_main.set_ylim(dv_limits[0] - pady, dv_limits[1] + pady)

    # Create histogram for lr_data
    ax_hist_lr = fig.add_subplot(gs[0, 0:3], sharex=ax_main)  # Histogram for x
    ax_hist_lr.hist(lr_data, bins=30, color='black', edgecolor='black')
    ax_hist_lr.set_title('Left-Right Axis')
    ax_hist_lr.set_ylabel('Cell Density')
    ax_hist_lr.invert_xaxis()
    ax_hist_lr.xaxis.set_visible(False)
    ax_hist_lr.axvline(x=5700, color="black", linestyle=":")

    # Create histogram for dv_data
    ax_hist_dv = fig.add_subplot(gs[1:4, 3], sharey=ax_main)  # Histogram for y
    ax_hist_dv.hist(dv_data, bins=30, orientation='horizontal', color='black', edgecolor='black')
    ax_hist_dv.set_title('Dorsal-Ventral Axis')
    ax_hist_dv.set_xlabel('Cell Density')
    ax_hist_dv.invert_yaxis()
    ax_hist_dv.yaxis.set_visible(False)

    # Set labels and title for the main plot
    ax_main.set_ylabel('Dorsal-Ventral Axis')
    ax_main.set_xlabel('Left-Right Axis')

    # Adjust layout to prevent overlap and equalize spacing
    plt.tight_layout()

    if save_dir is not None:
        if bin_edges is not None:
            bin_range = f"{bin_edges[0]}-{bin_edges[1]}"
            plt.savefig(os.path.join(save_dir, f"heatmap_{bin_range}.jpg"), dpi=300)
        else:
            plt.savefig(os.path.join(save_dir, "ap_condensed.jpg"), dpi=300)"""


def plot_shadowed_heatmap(
        ax_lrdv,
        ax_rcdv,
        rc_data,
        lr_data,
        dv_data,
        rc_shadow,
        lr_shadow,
        dv_shadow,
        rc_limits,
        lr_limits,
        dv_limits,
        bin_edges=None,
        binned_lr_data = None,
        binned_dv_data = None,
        binned_lr_shadow = None,
        binned_dv_shadow = None
):

    print(lr_shadow)
    print(dv_shadow)

    # LRDV Heatmap ________________________________________________________________________________________________________________
    if bin_edges is not None:
        shadow_hist_lrdv, xedges_lrdv, yedges_lrdv = np.histogram2d(
            binned_lr_shadow,
            binned_dv_shadow,
            bins=150,
            range=[[lr_limits[0], lr_limits[1]], [dv_limits[0], dv_limits[1]]]
        )
        shadow_hist_lrdv = gaussian_filter(shadow_hist_lrdv, sigma=1)
        extent_lrdv = [xedges_lrdv[0], xedges_lrdv[-1], yedges_lrdv[0], yedges_lrdv[-1]]
        ax_lrdv.imshow(np.rot90(shadow_hist_lrdv), cmap="Greys", extent=extent_lrdv, aspect='auto')

        # determine the number of cells
        n_cells = len(binned_lr_data)

        # Data
        try:
            xy_data_lrdv = np.vstack([binned_lr_data, binned_dv_data])
            kde_data_lrdv = gaussian_kde(xy_data_lrdv)
            xmin_lrdv, xmax_lrdv = lr_limits
            ymin_lrdv, ymax_lrdv = dv_limits
            x_lrdv, y_lrdv = np.mgrid[xmin_lrdv:xmax_lrdv:100j, ymin_lrdv:ymax_lrdv:100j]
            positions_data_lrdv = np.vstack([x_lrdv.ravel(), y_lrdv.ravel()])
            z_lrdv = np.reshape(kde_data_lrdv(positions_data_lrdv).T, x_lrdv.shape)
            custom_cmap = create_transparent_bottomed_cmap('plasma')
            ax_lrdv.imshow(np.rot90(z_lrdv), cmap=custom_cmap, extent=[xmin_lrdv, xmax_lrdv, ymin_lrdv, ymax_lrdv], aspect='auto')
        except:
            pass

        ax_lrdv.axvline(x=5700, color="black", linestyle=":")

        # Set axis limits
        padx_lrdv = 1000
        pady_lrdv = 1000
        ax_lrdv.set_xlim(lr_limits[0] - padx_lrdv, lr_limits[1] + padx_lrdv)
        ax_lrdv.set_ylim(dv_limits[0] - pady_lrdv, dv_limits[1] + pady_lrdv)

        # Set axis labels
        ax_lrdv.set_ylabel('Dorsal-Ventral Axis um')
        ax_lrdv.set_xlabel('Left-Right Axis um')

        # invert axes
        ax_lrdv.invert_yaxis()
        ax_lrdv.invert_xaxis()

        return n_cells

    else:
        shadow_hist_lrdv, xedges_lrdv, yedges_lrdv = np.histogram2d(
            lr_shadow,
            dv_shadow,
            bins=150,
            range=[[lr_limits[0], lr_limits[1]], [dv_limits[0], dv_limits[1]]]
        )
        shadow_hist_lrdv = gaussian_filter(shadow_hist_lrdv, sigma=1)
        extent_lrdv = [xedges_lrdv[0], xedges_lrdv[-1], yedges_lrdv[0], yedges_lrdv[-1]]
        ax_lrdv.imshow(np.rot90(shadow_hist_lrdv), cmap="Greys", extent=extent_lrdv, aspect='auto')

        # Data
        try:
            xy_data_lrdv = np.vstack([lr_data, dv_data])
            kde_data_lrdv = gaussian_kde(xy_data_lrdv)
            xmin_lrdv, xmax_lrdv = lr_limits
            ymin_lrdv, ymax_lrdv = dv_limits
            x_lrdv, y_lrdv = np.mgrid[xmin_lrdv:xmax_lrdv:100j, ymin_lrdv:ymax_lrdv:100j]
            positions_data_lrdv = np.vstack([x_lrdv.ravel(), y_lrdv.ravel()])
            z_lrdv = np.reshape(kde_data_lrdv(positions_data_lrdv).T, x_lrdv.shape)
            custom_cmap = create_transparent_bottomed_cmap('plasma')
            ax_lrdv.imshow(np.rot90(z_lrdv), cmap=custom_cmap, extent=[xmin_lrdv, xmax_lrdv, ymin_lrdv, ymax_lrdv], aspect='auto')
        except:
            pass

        ax_lrdv.axvline(x=5700, color="black", linestyle=":")

        # Set axis limits
        padx_lrdv = 1000
        pady_lrdv = 1000
        ax_lrdv.set_xlim(lr_limits[0] - padx_lrdv, lr_limits[1] + padx_lrdv)
        ax_lrdv.set_ylim(dv_limits[0] - pady_lrdv, dv_limits[1] + pady_lrdv)

        # Set axis labels
        ax_lrdv.set_ylabel('Dorsal-Ventral Axis um')
        ax_lrdv.set_xlabel('Left-Right Axis um')

        # invert axes
        ax_lrdv.invert_yaxis()
        ax_lrdv.invert_xaxis()

    # RCDV Heatmap ________________________________________________________________________________________________________________
    shadow_hist_rcdv, xedges_rcdv, yedges_rcdv = np.histogram2d(
        rc_shadow,
        dv_shadow,
        bins=150,
        range=[[rc_limits[0], rc_limits[1]], [dv_limits[0], dv_limits[1]]]
    )
    shadow_hist_rcdv = gaussian_filter(shadow_hist_rcdv, sigma=1)
    extent_rcdv = [xedges_rcdv[0], xedges_rcdv[-1], yedges_rcdv[0], yedges_rcdv[-1]]
    ax_rcdv.imshow(np.rot90(shadow_hist_rcdv), cmap="Greys", extent=extent_rcdv, aspect='auto')

    # Data Heatmap for second heatmap
    xy_data_rcdv = np.vstack([rc_data, dv_data])
    kde_data_rcdv = gaussian_kde(xy_data_rcdv)
    xmin_rcdv, xmax_rcdv = rc_limits
    ymin_rcdv, ymax_rcdv = dv_limits
    x_rcdv, y_rcdv = np.mgrid[xmin_rcdv:xmax_rcdv:100j, ymin_rcdv:ymax_rcdv:100j]
    positions_data_rcdv = np.vstack([x_rcdv.ravel(), y_rcdv.ravel()])
    z_rcdv = np.reshape(kde_data_rcdv(positions_data_rcdv).T, x_rcdv.shape)
    custom_cmap_rcdv = create_transparent_bottomed_cmap('plasma')
    ax_rcdv.imshow(np.rot90(z_rcdv), cmap=custom_cmap_rcdv, extent=[xmin_rcdv, xmax_rcdv, ymin_rcdv, ymax_rcdv], aspect='auto')

    # Set axis limits of 2D heatmap
    padx_rcdv = 1000
    pady_rcdv = 1000
    ax_rcdv.set_xlim(rc_limits[0] - padx_rcdv, rc_limits[1] + padx_rcdv)
    ax_rcdv.set_ylim(dv_limits[0] - pady_rcdv, dv_limits[1] + pady_rcdv)

    # Set axis labels
    ax_rcdv.set_xlabel('Rostral-Caudal Axis um')
    ax_rcdv.invert_yaxis()

