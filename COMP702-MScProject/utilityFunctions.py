# contains functions for creating plots for MSc Project phyics informed
# neural networks

import numpy as np
import torch
import matplotlib.pyplot as plt

# create 2d arrays of solution and residual
# input:
# model to compute solution and residual from 2 inputs only
# x and y dimensions of solution space (points at which to compute)
# min and max extents of x and y axes respectively
# output:
# x and y - 2D numpy arrays and size y*x
# u, 2D numpy array containing PINN approximated solution for all points
# within mesh
# r, 2D numpy array containing computed residual for all points within mesh
def create2dMeshData(model, xDim, yDim, xMin, xMax, yMin, yMax):

    # create np arrays based on input domain extent and dimensions of mesh
    x = np.arange(xMin, xMax, (xMax-xMin)/xDim)
    y = np.arange(yMin, yMax, (yMax-yMin)/yDim)
    # create meshgrid arrays
    xArray, yArray = np.meshgrid(x, y)

    # create empty array to contain all meshgrid points
    flattenedCoords = np.zeros(((xDim)*(yDim), 2))
    # add meshgrid points
    flattenedCoords[:,0] = xArray.flatten()
    flattenedCoords[:,1] = yArray.flatten()
    # convert numpy array to pytorch tensor
    flattenedCoords = torch.from_numpy(flattenedCoords.astype(np.float32))

    # use PINN to approximate solution for all points
    flattened_uArray = model(flattenedCoords[:,0], flattenedCoords[:,1])
    # reshape solution array into meshgrid shape and convert to numpy
    uArray = torch.reshape(
        flattened_uArray,(yDim, xDim)).detach().numpy()

    # compute residual at all points
    flattened_rArray = model.residual(
        flattenedCoords[:,0].requires_grad_(),
        flattenedCoords[:,1].requires_grad_())
    # reshape residual array into meshgrid shape and convert to numpy
    rArray = torch.reshape(
        flattened_rArray, (yDim, xDim)).detach().numpy()

    return xArray, yArray, uArray, rArray


# returns training history plot
# input:
# history, numpy array - epochs in first dimension
# variableNamesList, list containing names of variables as strings for legend
# plotTitle, string
# yLogAx, boolean indicating whether y (loss) axis uses a log scale
# insetDetail, boolean indicating whether or not to include inset axis of
# last quarter of training epochs
# insetLoc, list indication location of inset ax
# warning: do not use both log loss ax and inset detail
# returns: figure
def trainingHistoryPlot(history, variableNamesList, yAxisLabel, plotTitle, yLogAx=True,
insetDetail=False, insetLoc=[0.5, 0.5, 0.46, 0.42]):
    fig, ax = plt.subplots(figsize=(6,4))
    # plot losses
    for idx, variableName in enumerate(variableNamesList):
        ax.plot(history[:,idx], label=variableName)
    # check for log loss axis
    if yLogAx:
        ax.set_yscale('log')
    # add legend
    ax.legend(loc=(1.01, 0.5))
    # label axes
    ax.set_xlabel('Epoch')
    ax.set_ylabel(yAxisLabel)
    # figure title
    fig.suptitle(plotTitle, fontsize=16)

    if insetDetail:
        # add an insert ax in top right corner
        axins = ax.inset_axes(insetLoc)
        # plot losses on insert ax
        for idx in range(variableNamesList):
            axins.plot(history[:,idx])
        # set limits of insert ax
        axins.set_xlim(3*history.shape[0]//4, history.shape[0])
        axins.set_ylim(0, history[3*history.shape[0]//4:].max())
        # remove x axis labels
        axins.set_xticklabels([])
        # add insert locator lines
        ax.indicate_inset_zoom(axins, edgecolor='black')
    return fig
