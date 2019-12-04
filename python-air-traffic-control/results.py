import numpy as np
import matplotlib.pyplot as plt

def displayScores():
    loss = np.load("score.npy")
    epochs = np.linspace(0, len(loss), num=len(loss))
    plt.title('Scores Over Time')
    plt.xlabel("Epochs")
    plt.ylabel('Score')
    plt.plot(epochs, loss)
    plt.show()

if __name__=="__main__":
    displayScores()