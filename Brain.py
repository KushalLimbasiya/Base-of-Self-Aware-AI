"""Neural network architecture for Atom intent classification.

This module defines the feedforward neural network used for
classifying user intents from tokenized speech input.
"""

import torch.nn as nn 

class NeuralNet(nn.Module):
    """Feedforward neural network for intent classification.
    
    A 3-layer fully connected neural network with ReLU activations
    for classifying user intents from bag-of-words input.
    
    Architecture:
        - Input layer → Hidden layer 1 (ReLU)
        - Hidden layer 1 → Hidden layer 2 (ReLU)
        - Hidden layer 2 → Output layer (no activation)
    
    Attributes:
        l1 (nn.Linear): First linear layer
        l2 (nn.Linear): Second linear layer
        l3 (nn.Linear): Output layer
        relu (nn.ReLU): ReLU activation function
    """

    def __init__(self, input_size, hidden_size, num_classes):
        """Initialize the neural network.
        
        Args:
            input_size (int): Size of input features (vocabulary size)
            hidden_size (int): Number of neurons in hidden layers
            num_classes (int): Number of output classes (intent tags)
        """
        super(NeuralNet,self).__init__()
        self.l1 = nn.Linear(input_size,hidden_size)
        self.l2 = nn.Linear(hidden_size,hidden_size)
        self.l3 = nn.Linear(hidden_size,num_classes)
        self.relu = nn.ReLU()

    def forward(self, x):
        """Forward pass through the network.
        
        Args:
            x (torch.Tensor): Input tensor of shape (batch_size, input_size)
        
        Returns:
            torch.Tensor: Output logits of shape (batch_size, num_classes)
        """
        out = self.l1(x)
        out = self.relu(out)
        out = self.l2(out)
        out = self.relu(out)
        out = self.l3(out)
        return out


