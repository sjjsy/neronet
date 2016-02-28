import matplotlib.pyplot as plt

def reader(line):
    keys = ['identity', 'squared', 'cubed']
    vals = [int(val) for val in line.strip().split(', ') if val]
    return dict(zip(keys, vals))

def plot(filename, name, x, y):
    fig, ax = plt.subplots(nrows=1, ncols=1)
    ax.plot(x, y)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('%s' % (name))
    fig.savefig(filename)
    plt.close(fig)
