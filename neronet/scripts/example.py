""" A module containing example functions for reading and plotting user output

It is important to make sure the functions work as the error messages can be 
varied and messy to handle. The software raises ImportError if there is 
something wrong with importing or running the code.
"""
import matplotlib.pyplot as plt

def line_reader(line, names, sep=', ', *args):
    """ Maps a line of output to names given as string
    
    Parameters:
        line (str): a line of the output file
        names (str): names of the output file data as a string
        sep (str): separator for the data in the line
    
    Returns:
        dict: The data in the line mapped to the names
    """
    #Takes names and splits it to keys corresponding to each value in the line
    keys = names.split()
    #Splits the line and casts them as integers
    vals = [float(val) for val in line.strip().split(sep)]
    #Maps the values to the keys and makes a dictionary
    return dict(zip(keys, vals))

def file_reader(output_file, names, sep=', ', *args):
    """ Maps a line of output to names given as string
    
    Parameters:
        output_file (file object): output file file object
        names (str): names of the output file data
        sep (str): separator for the data in the line
    
    Returns:
        dict: The data in the line mapped to the names
    """
    file_data = output_file.read().strip().split('\n')
    keys = names.split()
    data = {}
    for key in keys:
        data[key] = []
    for line in file_data:
        vals = [float(val) for val in line.strip().split(sep)]
        for key, val in zip(keys, vals):
            data[key].append(val)
    return data

def plot(filename, feedback, save_image, y, x=None, *args):
    """ Plots the given values to file

    Parameters:
        filename (str): name of the file where the plot is saved
        x (list): values of the x component
        y (list): values of the y component
        ax2: (axes object): axes object containing previous axes data

    Returns:
        axes object: an axes object that can be used to combine the plots
    """
    if not x:
        x = ('x', [i for i in range(len(y[1]))])
    if feedback:
        #Adds the plot to the combined axes
        feedback.plot(x[1],y[1])
        if save_image:
            fig = feedback.get_figure()
            fig.savefig(filename)
        return feedback
    else:
        #Creates and plots the current figure
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(x[1],y[1])
        ax.set_xlabel(x[0])
        ax.set_ylabel(y[0])
        if save_image:
            fig.savefig(filename)
        return ax
