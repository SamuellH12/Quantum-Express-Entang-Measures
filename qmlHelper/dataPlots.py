from matplotlib import pyplot as plt
import numpy as np
from .utils import classifier
from .metrics import threshold

PLT_MARKERS = ['o', 's', '^', 'v', '<', '>', 'p', '*', 'h', 'H', 'D', 'd']

def print2D_decision_region(circuit, weights, bias, data, labels, circuit_params, num_classes, supervised = False,
                            grid_colormap = 'inferno', data_colormap = 'viridis', 
                            x_max=2*np.pi, y_max=2*np.pi, x_min=0.0, y_min=0.0, figsize=(6, 4), resolution=20):

    # make data for decision regions and preprocess grid pointss
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, resolution), np.linspace(y_min, y_max, resolution))
    X_grid = np.c_[xx.ravel(), yy.ravel()]
    features_grid = np.array( [list(x) + list(x)[:max(0, len(data[0])-len(x))] for x in X_grid] )  # angles for state preparation are new features // extend the len of features if less than
    predictions_grid = np.array([classifier(circuit, Xi, weights, bias, circuit_params) for Xi in features_grid ])
    Z = predictions_grid.reshape(xx.shape)

    # Plot
    plt.figure(figsize=figsize)

    plt.contourf(xx, yy, Z, levels=np.arange(-1.5, 1.6, 0.1), cmap=grid_colormap, alpha=0.8 ) # decision regions
    plt.contour( xx, yy, Z, levels=np.arange(-1, 1 + 2/num_classes, 2/num_classes), colors='k', linestyles='--', linewidths=0.5) # decision boundaries
    # cnt = plt.contourf( xx, yy, Z, levels=np.arange(-1, 1.1, 0.1), cmap=cm, alpha=0.8, extend="both" )
    # plt.contour(        xx, yy, Z, levels=[-1.0, -threshold_div, 0.0, threshold_div, 1.0], colors=("black",), linestyles=("--",), linewidths=(0.8,))
    
    label_predict = np.array([threshold(classifier(circuit, Xi, weights, bias, circuit_params), num_classes) for Xi in data ])
    data_cmap = plt.get_cmap(data_colormap, max(num_classes, len(set(labels)), len(set(label_predict))) * 2)

    # Plot points
    if supervised:
        for class_idx in set(labels):
            correct_mask   = (labels == class_idx) & (label_predict == class_idx)
            incorrect_mask = (labels == class_idx) & (label_predict != class_idx)
            
            plt.scatter(data[correct_mask,   0], data[correct_mask,   1], c=[data_cmap(class_idx*2)],   marker=PLT_MARKERS[class_idx], edgecolor='k', s=100) # Points correctly classified
            plt.scatter(data[incorrect_mask, 0], data[incorrect_mask, 1], c=[data_cmap(class_idx*2+1)], marker=PLT_MARKERS[class_idx], edgecolor='k') # Points misclassified
    else:
        for class_idx in set(label_predict):
            for class_lbl in set(labels):
                this_mask = (label_predict == class_idx) & (labels == class_lbl)
                plt.scatter(data[this_mask, 0],   data[this_mask, 1], c=[data_cmap(class_idx*2)], marker=PLT_MARKERS[class_lbl*2+1], edgecolor='k', s=50, label=f'Class {class_idx} | Label {class_lbl}') # Points correctly classified

    
    # define limits
    plt.xlim(xx.min(), xx.max())
    plt.ylim(yy.min(), yy.max())
    plt.title(f"Decision regions ({num_classes} classes)")
    
    # Create colorbar
    cbar = plt.colorbar(ticks=np.arange(num_classes))
    cbar.set_label('Class')
    cbar.set_ticklabels(np.arange(num_classes))
    
    
    plt.legend(bbox_to_anchor=(1.1, 1), loc='upper left')
    plt.tight_layout()
    plt.show()





from matplotlib.colors import ListedColormap
from scipy.interpolate import griddata


def print2D_decision_region_multiclass(circuit, weights, bias, data, labels, circuit_params, 
                          num_classes=2, colormap='viridis', 
                          x_max=2*np.pi, y_max=2*np.pi, x_min=0.0, y_min=0.0,
                          resolution=100):

    print('!!! não finalizado ainda !!!')
    a = 1 / 0

    # Create high-resolution mesh grid
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, resolution), np.linspace(y_min, y_max, resolution))
    X_grid = np.c_[xx.ravel(), yy.ravel()]
    
    # Get predictions for each grid point
    raw_predictions = np.array([classifier(circuit, Xi, weights, bias, circuit_params) for Xi in X_grid])
    class_predictions = np.array([threshold(pred, num_classes) for pred in raw_predictions])
    
    # For smooth visualization, we'll create continuous values for the colormap
    if num_classes == 2:
        # For binary, use the raw prediction values directly
        Z = raw_predictions.reshape(xx.shape)
    else:
        # For multi-class, create smooth interpolation between class centers
        class_centers = np.linspace(0, 1, num_classes)
        Z = griddata(X_grid, class_centers[class_predictions], (xx, yy), method='cubic', fill_value=0)
        # from scipy.ndimage import gaussian_filter
        # Z = gaussian_filter(Z, sigma=resolution*smoothness/100)
    
    # Create figure
    plt.figure(figsize=(8, 6))
    
    # Custom colormaps for different class counts
    colors = plt.get_cmap(colormap)(np.linspace(0, 1, num_classes))
    cmap = ListedColormap(colors)
    levels = np.linspace(0, 1, num_classes*20)
    
    # Plot decision regions with smooth contours
    contour = plt.contourf(xx, yy, Z, levels=levels, cmap=cmap, alpha=0.8)

    boundary_levels = np.linspace(0.5/num_classes, 1-0.5/num_classes, num_classes-1)
    plt.contour(xx, yy, Z, levels=boundary_levels, colors='k', linestyles='--', linewidths=1)
    
    # Get predictions for training data
    train_raw = np.array([classifier(circuit, Xi, weights, bias, circuit_params) for Xi in data])
    train_pred = np.array([threshold(pred, num_classes) for pred in train_raw])
    
    # Markers and colors for classes
    markers = PLT_MARKERS[:num_classes]
    colors = cmap(np.linspace(0, 1, num_classes))
    
    for class_idx in range(num_classes):
        correct   = (labels == class_idx) & (train_pred == class_idx)
        incorrect = (labels == class_idx) & (train_pred != class_idx)
        
        # Correct predictions
        plt.scatter(data[correct, 0], data[correct, 1], c=[colors[class_idx]], marker=markers[class_idx],
                   edgecolor='k', s=60, label=f'Class {class_idx} (correct)')
        
        # Incorrect predictions
        plt.scatter(data[incorrect, 0], data[incorrect, 1], c='red', marker=markers[class_idx],
                   edgecolor='k', s=80, label=f'Class {class_idx} (wrong)')
    
    # Add colorbar
    cbar = plt.colorbar(contour, ticks=np.linspace(0.5/num_classes, 1-0.5/num_classes, num_classes))
    cbar.set_ticklabels([f'Class {i}' for i in range(num_classes)])
    
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    plt.title(f"Smooth Decision Regions ({num_classes} classes)")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()