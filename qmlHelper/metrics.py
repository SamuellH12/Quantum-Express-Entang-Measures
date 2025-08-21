from pennylane import numpy as np

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

        for i in range(num_classes):
            if boundaries[i] <= output < boundaries[i+1]:
               return i
        return 0 if output < boundaries[0] else num_classes-1

    # multiple qubits
    if len(output) == num_classes:
        max_val = max(output)
        for i, val in enumerate(output):
            if val == max_val:
               return i
        return num_classes-1
    
    raise ValueError(f"Cannot map {output.size} measurement(s) to {num_classes} classes")

def normalize_0_n(output, num_classes=2):
    if len(output) == 1: # [-1, 1]
        output = output[0]
        output = (output+1)/2 #[0, 1]
        return output*(num_classes-1) #[0, num_classes-1]
    
    raise ValueError(f"Cannot map {output.size} measurements to [0, {num_classes-1}] interval")

from sklearn.metrics.cluster import silhouette_score
from sklearn.metrics import rand_score, davies_bouldin_score, calinski_harabasz_score


def square_loss_silhouette(features, predictions, labels, num_classes):
  if(len(predictions) == 1): predictions = np.reshape(predictions, (len(predictions[0]), 1))
  predictions = np.array([ threshold(pred, num_classes) for pred in predictions ])
  if len(np.unique(predictions)) == 1: return np.float64(1)
  return np.float64(1 - silhouette_score(features, predictions))

def square_loss_davies_bouldin_score(features, predictions, labels, num_classes):
  if(len(predictions) == 1): predictions = np.reshape(predictions, (len(predictions[0]), 1))
  predictions = np.array([ threshold(pred, num_classes) for pred in predictions ])
  if len(np.unique(predictions)) == 1: return np.float64(1)
  return np.float64(davies_bouldin_score( features, predictions))

def square_loss_calinski_harabasz_score(features, predictions, labels, num_classes):
  if(len(predictions) == 1): predictions = np.reshape(predictions, (len(predictions[0]), 1))
  predictions = np.array([ threshold(pred, num_classes) for pred in predictions ])
  if len(np.unique(predictions)) == 1: return np.float64(10)
  return np.float64( 1.0 / (1e-5 + calinski_harabasz_score(features, predictions))) # original [0, INF) where INF is better


from sklearn.metrics import adjusted_rand_score
from . import utils as qmlHelperUtils

def unsupervised_accuracy(circuit, weights, bias, data, label, num_classes, circuit_args = {'encoding': 'phase', 'meas' : 'expval', 'measwire': [0]}):
   
   predictions = np.array([qmlHelperUtils.classifier(circuit, Xi, weights, bias, circuit_args) for Xi in data ] )
   predictions = np.array([ threshold(pred, num_classes) for pred in predictions ])
   
   return adjusted_rand_score(label, predictions)


from pennylane import math as qmlMath

def squared_loss_supervised(features, predictions, labels, num_classes):
  if(len(predictions) == 1): predictions = np.reshape(predictions, (len(predictions[0]), 1))
  predictions = np.array([ normalize_0_n(pred, num_classes) for pred in predictions ])
  return np.mean( (labels - qmlMath.stack(predictions)) ** 2)
