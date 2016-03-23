""" A module containing example functions for reading and plotting user output

It is important to make sure the functions work as the error messages can be 
varied and messy to handle. The software raises ImportError if there is 
something wrong with importing or running the code.
"""
import matplotlib.pyplot as plt

def reader(line, names):
    """ Maps a line of output to names given as string
    
    Parameters:
        line (str): a line of the output file
        names (str): names of the output file data
    
    Returns:
        dict: The data in the line mapped to the names
    """
    #Takes names and splits it to keys corresponding to each value in the line
    keys = names.split()
    #Splits the line and casts them as integers
    vals = [int(val) for val in line.strip().split(', ') if val]
    #Maps the values to the keys and makes a dictionary
    return dict(zip(keys, vals))

def plot(filename, feedback, x, y):
    """ Plots the given values to file

    Parameters:
        filename (str): name of the file where the plot is saved
        x (list): values of the x component
        y (list): values of the y component
        ax2: (axes object): axes object containing previous axes data

    Returns:
        axes object: an axes object that can be used to combine the plots
    """
    #Creates and plots the current figure
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(x,y)
    fig.savefig(filename)
    
    if feedback:
        #Adds the plot to the combined axes
        feedback.plot(x,y)
        return feedback
    else:
        return ax