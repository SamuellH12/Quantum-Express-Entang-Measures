from pennylane import numpy as np
import pennylane as qml
from pennylane.optimize import NesterovMomentumOptimizer, RotosolveOptimizer, GradientDescentOptimizer, SPSAOptimizer
from . import dataPlots as localDataPlots
from . import metrics as qmlHelperMetrics 


def classifier(circuit : callable, X_data : list, weights : list = [], bias : list = 0, circuit_args = {'encoding': 'phase', 'meas' : 'expval', 'measwire': [0]}):
        return np.array(circuit(weights=weights, input=X_data, **circuit_args)) + np.array(bias)

def cost(circuit, weights, bias, metric, X_batch, y_batch, num_classes, circuit_args = {'encoding': 'phase', 'meas' : 'expval', 'measwire': [0]}):
    predictions = np.array([classifier(circuit, Xi, weights, bias, circuit_args) for Xi in X_batch ] )
    return metric(X_batch, predictions, y_batch, num_classes)



def train_ansatz(circuit : callable, n_params : int, 
                 circuit_args : dict, data, labels, 
                 batch_size = 10, Steps = 100, 
                 cost_metric = qmlHelperMetrics.square_loss_silhouette, 
                 opt = SPSAOptimizer(10), 
                 seed=12, threshold_n_classes = 2, use_bias = True,
                 print_cost_interval = -1, print_decision_region = False
                ):
  np.random.seed(seed)
  
  weights = np.random.randn(n_params, requires_grad=True)
  bias = np.array([0.0], requires_grad=True)

  for i in range(Steps):
    idxs = np.random.randint(0, len(data), (batch_size,))
    x_batch = data[idxs]
    y_batch = labels[idxs]

    arguments = [circuit, weights, bias if use_bias else np.array(0) , cost_metric, x_batch, y_batch, threshold_n_classes, circuit_args]
    weights, _bias_ = opt.step(cost, *arguments)[1:3] #be carefull here. W and B are really [1] and [2]???
    if use_bias: bias = _bias_

    if print_cost_interval > 0 and (i % print_cost_interval == 0 or i == Steps-1):
        arguments = [circuit, weights, bias, cost_metric, data, labels, threshold_n_classes, circuit_args]
        print(f'{i+1}/{Steps} | Cost: {cost(*arguments)}')
        if print_decision_region == True: 
            localDataPlots.print2D_decision_region(circuit, weights, bias, data, labels, circuit_args, threshold_n_classes)

  return weights, bias

