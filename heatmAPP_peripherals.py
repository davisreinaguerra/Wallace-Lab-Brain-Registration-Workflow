import os
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import easygui
from scipy.stats import gaussian_kde
from scipy.ndimage import gaussian_filter
import tkinter as tk
import easygui

def create_transparent_bottomed_cmap(predefined_cmap_name):
    default_cmap = plt.get_cmap(predefined_cmap_name)
    ncolors = default_cmap.N

    # Create a gradient from transparent to the colors of the original colormap
    transparent_colors = np.zeros((ncolors, 4))
    transparent_colors[:, 0:3] = default_cmap(np.linspace(0, 1, ncolors))[:, 0:3]  # Get RGB values
    transparent_colors[:, 3] = np.linspace(0, 1, ncolors)  # Alpha from 0 (transparent) to 1 (opaque)

    # Create the final colormap
    return ListedColormap(transparent_colors)

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
        cmap_template,
        bin_edges,
        binned_lr_data,
        binned_dv_data,
        binned_lr_shadow,
        binned_dv_shadow,
        global_max,
        global_min,
        global_max_scaler
):

    # for manual control
    config_shadow_bins = 200
    config_shadow_sigma = 1
    config_data_bins = 100
    config_data_sigma = 2
    config_padx = 300;
    config_pady = 300;
    config_shadow_color = "Greys"

    if bin_edges is not None:

        bin_size = bin_edges[1] - bin_edges[0]
        binsize_reciprocal = 1 / (bin_size / 1000)
        #print(binsize_reciprocal)

        # Create Binned Shadow
        shadow_hist_lrdv, xedges_lrdv, yedges_lrdv = np.histogram2d(
            binned_lr_shadow,
            binned_dv_shadow,
            bins=config_shadow_bins,
            range=[[lr_limits[0], lr_limits[1]], [dv_limits[0], dv_limits[1]]]
        )
        shadow_hist_lrdv = gaussian_filter(shadow_hist_lrdv, sigma=config_shadow_sigma)
        extent_lrdv = [xedges_lrdv[0], xedges_lrdv[-1], yedges_lrdv[0], yedges_lrdv[-1]]
        # Show Binned Shadow
        ax_lrdv.imshow(
            np.rot90(shadow_hist_lrdv),
            cmap=config_shadow_color,
            extent=extent_lrdv,
            aspect='auto'
        )

        # Create Binned Data
        try:
            data_hist_lrdv, xedges_lrdv, yedges_lrdv = np.histogram2d(
                binned_lr_data,
                binned_dv_data,
                bins=config_data_bins,
                range=[[lr_limits[0], lr_limits[1]], [dv_limits[0], dv_limits[1]]]
            )
            data_hist_lrdv = gaussian_filter(data_hist_lrdv, sigma=config_data_sigma)
            extent_lrdv = [xedges_lrdv[0], xedges_lrdv[-1], yedges_lrdv[0], yedges_lrdv[-1]]
            custom_cmap = create_transparent_bottomed_cmap(cmap_template)
            # Show Binned Data
            ax_lrdv.imshow(
                np.rot90(data_hist_lrdv),
                cmap=custom_cmap,
                extent=extent_lrdv,
                aspect='auto',
                vmin = global_min,
                vmax = (global_max * global_max_scaler)
            )

        except:
            print("didnt work")
            pass

    else:
        # Full Shadow
        shadow_hist_lrdv, xedges_lrdv, yedges_lrdv = np.histogram2d(
            lr_shadow,
            dv_shadow,
            bins=config_shadow_bins,
            range=[[lr_limits[0], lr_limits[1]], [dv_limits[0], dv_limits[1]]]
        )
        shadow_hist_lrdv = gaussian_filter(shadow_hist_lrdv, sigma=config_shadow_sigma)
        extent_lrdv = [xedges_lrdv[0], xedges_lrdv[-1], yedges_lrdv[0], yedges_lrdv[-1]]
        ax_lrdv.imshow(np.rot90(shadow_hist_lrdv), cmap=config_shadow_color, extent=extent_lrdv, aspect='auto')

        # Full Data
        try:
            data_hist_lrdv, xedges_lrdv, yedges_lrdv = np.histogram2d(
                lr_data,
                dv_data,
                bins=config_data_bins,
                range=[[lr_limits[0], lr_limits[1]], [dv_limits[0], dv_limits[1]]]
            )
            data_hist_lrdv = gaussian_filter(data_hist_lrdv, sigma=config_data_sigma)
            extent_lrdv = [xedges_lrdv[0], xedges_lrdv[-1], yedges_lrdv[0], yedges_lrdv[-1]]
            custom_cmap = create_transparent_bottomed_cmap(cmap_template)
            ax_lrdv.imshow(
                np.rot90(data_hist_lrdv),
                cmap=custom_cmap,
                extent=extent_lrdv,
                aspect='auto'
            )
        except:
            pass

    """
    RCDV_____________________________________________________________________________________________________________"""

    # Shadow
    shadow_hist_rcdv, xedges_rcdv, yedges_rcdv = np.histogram2d(
        rc_shadow,
        dv_shadow,
        bins=config_shadow_bins,
        range=[[rc_limits[0], rc_limits[1]], [dv_limits[0], dv_limits[1]]]
    )
    shadow_hist_rcdv = gaussian_filter(shadow_hist_rcdv, sigma=config_shadow_sigma)
    extent_rcdv = [xedges_rcdv[0], xedges_rcdv[-1], yedges_rcdv[0], yedges_rcdv[-1]]
    ax_rcdv.imshow(
        np.rot90(shadow_hist_rcdv),
        cmap=config_shadow_color,
        extent=extent_rcdv,
        aspect='auto'
    )

    # Data
    data_hist_rcdv, xedges_rcdv, yedges_rcdv = np.histogram2d(
        rc_data,
        dv_data,
        bins=config_data_bins,
        range=[[rc_limits[0], rc_limits[1]], [dv_limits[0], dv_limits[1]]]
    )
    data_hist_rcdv = gaussian_filter(data_hist_rcdv, sigma=config_data_sigma)
    extent_rcdv = [xedges_rcdv[0], xedges_rcdv[-1], yedges_rcdv[0], yedges_rcdv[-1]]
    custom_cmap = create_transparent_bottomed_cmap(cmap_template)
    img = ax_rcdv.imshow(
        np.rot90(data_hist_rcdv),
        cmap=custom_cmap,
        extent=extent_rcdv,
        aspect='auto'
    )

    """
    CONFIGURE AXES __________________________________________________________________________________________________"""

    # RCDV
    ax_rcdv.set_xlabel('Rostro-Caudal Axis (mm)')
    ax_rcdv.set_xlim(rc_limits[0] - config_padx, rc_limits[1] + config_padx)
    ax_rcdv.set_ylim(dv_limits[0] - config_pady, dv_limits[1] + config_pady)
    ax_rcdv.invert_yaxis()
    ax_rcdv.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x / 1000:g}'))
    ax_rcdv.set_yticks([])

    # LRDV
    ax_lrdv.set_ylabel('Dorsal-Ventral Axis (mm)')
    ax_lrdv.set_xlabel('Left-Right Axis (mm)')
    ax_lrdv.set_xlim(lr_limits[0] - config_padx, lr_limits[1] + config_padx)
    ax_lrdv.set_ylim(dv_limits[0] - config_pady, dv_limits[1] + config_pady)
    ax_lrdv.invert_yaxis()
    ax_lrdv.invert_xaxis()
    ax_lrdv.axvline(x=5700, color="black", linestyle=":")
    ax_lrdv.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x / 1000:g}'))
    ax_lrdv.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f'{y / 1000:g}'))
    