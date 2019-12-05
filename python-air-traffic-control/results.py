import numpy as np
import matplotlib.pyplot as plt

def displayScores():
    loss = np.load("episode_125score.npy")
    epochs = np.linspace(0, len(loss), num=len(loss))
    plt.figure(0)
    plt.title('Scores Over Time')
    plt.xlabel("Epochs")
    plt.ylabel('Score')
    plt.plot(epochs, loss)

    cumsum = np.cumsum(loss)
    avg = np.divide(cumsum, epochs+1)
    plt.figure(1)
    plt.title('Average Scores Over Time')
    plt.xlabel("Epochs")
    plt.ylabel('Average Score')
    plt.plot(epochs, avg)
    plt.show()

if __name__=="__main__":
    displayScores()
