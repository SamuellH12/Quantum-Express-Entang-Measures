import numpy as np

def get_hypercube(N: int):
    '''
    Args:
        N (int): Number of dimensions of the hypercube.
    Returns:
        np.ndarray: A (2^N, N) array containing the vertices of the hypercube.
    '''
    vertices = np.array(np.meshgrid(*[[0, 1]] * N)).T.reshape(-1, N)
    return (vertices - 0.5) * 2.0


def threshold(output, num_classes=2):
    """threshold function for multiple classes and measurements"""
    output = np.array(output)

    # only one qubit measured
    if len(output) == 1:
        boundaries = np.linspace(-1, 1, num_classes+1)
        return max(int(np.digitize(output, boundaries, right=True) - 1), 0)

    # multiple qubits
    if len(output) == num_classes:
        return int(np.argmax(output))
    
    raise ValueError(f"Cannot map {output.size} measurement(s) to {num_classes} classes")


from pennylane import numpy as np
from sklearn.metrics.cluster import silhouette_score
from sklearn.metrics import rand_score, davies_bouldin_score, calinski_harabasz_score


def square_loss_silhouette(features, predictions, labels, num_classes):
  if(len(predictions) == 1): predictions = np.array(predictions).reshape(len(predictions[0]), 1)
  predictions = np.array([ threshold(pred, num_classes) for pred in predictions ])
  if len(np.unique(predictions)) == 1: return np.float64(1)
  return np.float64(1 - silhouette_score(features, predictions))

def square_loss_davies_bouldin_score(features, predictions, labels, num_classes):
  if(len(predictions) == 1): predictions = np.array(predictions).reshape(len(predictions[0]), 1)
  predictions = np.array(list(map(threshold, predictions)))
  if len(np.unique(predictions)) == 1: return np.float64(1)
  return np.float64(davies_bouldin_score( features, predictions))

def square_loss_calinski_harabasz_score(features, predictions, labels, num_classes):
  if(len(predictions) == 1): predictions = np.array(predictions).reshape(len(predictions[0]), 1)
  predictions = np.array(list(map(threshold, predictions)))
  if len(np.unique(predictions)) == 1: return np.float64(10)
  return np.float64( 1.0 / (1e-5 + calinski_harabasz_score(features, predictions))) # original [0, INF) where INF is better
