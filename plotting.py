# plotting.py

import matplotlib as mpl
import matplotlib.backends.backend_pdf as mplpdf
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d as mpl3d
import numpy as np

import config as globals


def wavefunction1d(wavefunc, potential_vals, offset=0, scaling=1, ylabel='wavefunction', xlabel='x',
                         yrange=None, add_to_ax=None):
    x_vals = wavefunc.basis_labels
    if add_to_ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111)
    else:
        ax = add_to_ax
    ax.plot(x_vals, offset + scaling * wavefunc.amplitudes)
    if potential_vals is not None:
        ax.plot(x_vals, potential_vals)
        ax.plot(x_vals, [offset] * len(x_vals), 'b--')

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xlim(xmin=x_vals[0], xmax=x_vals[-1])
    if yrange is not None:
        ax.set_ylim(*yrange)
    if add_to_ax is None:
        plt.show()
    return None


def wavefunction1d_discrete(wavefunc, nrange, ylabel='wavefunction', xlabel='x'):
    x_vals = wavefunc.basis_labels
    width = .75
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.bar(x_vals, wavefunc.amplitudes, width=width)
    ax.set_xticks(x_vals + width / 2)
    ax.set_xticklabels(x_vals)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xlim(nrange)
    plt.show()
    return None


def wavefunction2d(wavefunc, figsize, aspect_ratio, zero_calibrate=False):
    min_vals = wavefunc.grid.min_vals
    max_vals = wavefunc.grid.max_vals

    plt.figure(figsize=figsize)
    if zero_calibrate:
        absmax = np.amax(np.abs(wavefunc.amplitudes))
        imshow_minval = -absmax
        imshow_maxval = absmax
        cmap = plt.get_cmap('PRGn')
    else:
        imshow_minval = np.min(wavefunc.amplitudes)
        imshow_maxval = np.max(wavefunc.amplitudes)
        cmap = plt.cm.viridis


    plt.imshow(wavefunc.amplitudes, extent=[min_vals[0], max_vals[0], min_vals[1], max_vals[1]],
               aspect=aspect_ratio, cmap=cmap, vmin=imshow_minval, vmax=imshow_maxval)
    plt.colorbar(fraction=0.017, pad=0.04)
    plt.show()
    return None


def contours(x_vals, y_vals, func, contour_vals=None, aspect_ratio=None, filename=None, 
        filled=False, contour_plot_function=plt.contourf, show_colorbar=True):
    """Contour plot of a 2d function 'func(x,y)'.
    x_vals: (ordered) list of x values for the x-y evaluation grid
    y_vals: (ordered) list of y values for the x-y evaluation grid
    func: function f(x,y) for which contours are to be plotted
    contour_values: contour values can be specified if so desired

    """
    x_grid, y_grid = np.meshgrid(x_vals, y_vals)
    z_array = func(x_grid, y_grid)
    # print(z_array)
    if aspect_ratio is None:
        plt.figure(figsize=(x_vals[-1] - x_vals[0], y_vals[-1] - y_vals[0]))
    else:
        w, h = plt.figaspect(aspect_ratio)
        plt.figure(figsize=(w, h))

    if contour_vals is None:
        contour_plot_function(x_grid, y_grid, z_array, cmap=plt.cm.viridis)
    else:
        contour_plot_function(x_grid, y_grid, z_array, levels=contour_vals, cmap=plt.cm.viridis)

    if show_colorbar:
        plt.colorbar()

    if filename:
        out_file = mplpdf.PdfPages(filename)
        out_file.savefig()
        out_file.close()
    return None


def matrixelements(mtable, mode='abs', xlabel='', ylabel='', zlabel=''):
    """Create a "skyscraper" and a color-coded plot of the matrix element table given as 'mtable'"""
    modefunction = globals.MODE_FUNC_DICT[mode]
    matsize = len(mtable)
    element_count = matsize**2   # num. of elements to plot
    xgrid, ygrid = np.meshgrid(range(matsize), range(matsize))
    xgrid = xgrid.T.flatten() - 0.5  # center bars on integer value of x-axis
    ygrid = ygrid.T.flatten() - 0.5  # center bars on integer value of y-axis
    zvals = np.zeros(element_count)       # all bars start at z=0
    dx = 0.75 * np.ones(element_count)      # width of bars in x-direction
    dy = dx.copy()      # width of bars in y-direction (same as x-dir here)
    dz = modefunction(mtable).flatten()  # height of bars from density matrix elements (should use 'real()' if complex)

    nrm = mpl.colors.Normalize(0, max(dz))   # <-- normalize colors to max. data
    colors = plt.cm.viridis(nrm(dz))  # list of colors for each bar

    # plot figure

    fig = plt.figure()
    ax = mpl3d.Axes3D(fig, azim=210, elev=43)
    ax.bar3d(xgrid, ygrid, zvals, dx, dy, dz, color=colors)
    ax.axes.w_xaxis.set_major_locator(plt.IndexLocator(1, -0.5))  # set x-ticks to integers
    ax.axes.w_yaxis.set_major_locator(plt.IndexLocator(1, -0.5))  # set y-ticks to integers
    ax.set_zlim3d([0, max(dz)])
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)

    cax, kw = mpl.colorbar.make_axes(ax, shrink=.75, pad=.02)  # add colorbar with normalized range
    cb1 = mpl.colorbar.ColorbarBase(cax, cmap=plt.cm.viridis, norm=nrm)
    plt.matshow(modefunction(mtable), cmap=plt.cm.viridis)
    plt.show()
    return None


def spectrum_with_matrixelement(spectrum_data, matrixelement_table, param_name='external parameter', energy_name='energy',
                                matrixelement_name='matrix element', norm_range=None, x_range=None, y_range=None,
                                colormap='jet', figsize=(15, 10), line_width=2):
    """Takes a list of x-values,
    a list of lists with each element containing the y-values corresponding to a particular curve,
    a list of lists with each element containing the external parameter value (t-value)
    that determines the color of each curve at each y-value,
    and a normalization interval for the t-values."""
    fig = plt.figure(figsize=figsize)

    if norm_range is None:
        norm_range=(np.min(matrixelement_table), np.max(matrixelement_table))

    for i in range(len(spectrum_data.energy_table[0])):
        pts = np.array([spectrum_data.param_vals, spectrum_data.energy_table[:,i]]).T.reshape(-1, 1, 2)
        segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
        line_collection = mpl.collections.LineCollection(segs, cmap=plt.get_cmap(colormap), norm=plt.Normalize(*norm_range))
        line_collection.set_array(matrixelement_table[:,i])
        line_collection.set_linewidth(line_width)
        plt.gca().add_collection(line_collection)

    plt.xlabel(param_name)
    plt.ylabel(energy_name)
    if not x_range:
        x_range = [np.amin(spectrum_data.param_vals), np.amax(spectrum_data.param_vals)]
    if not y_range:
        y_range = [np.amin(spectrum_data.energy_table), np.max(spectrum_data.energy_table)]


    plt.xlim(*x_range)
    plt.ylim(*y_range)

    axcb = fig.colorbar(line_collection)
    axcb.set_label(matrixelement_name)
    plt.show()