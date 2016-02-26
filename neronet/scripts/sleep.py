import matplotlib.pyplot as plt

def reader(line):
    keys = ['identity', 'squared', 'cubed']
    vals = [int(val) for val in line.strip().split(', ')]
    return dict(zip(keys, vals))

def plot(filename, x, y):
    fig, ax = plt.subplots(nrows=1, ncols=1)
    ax.plot(x, y)
    fig.savefig(filename)
    plt.close(fig)
