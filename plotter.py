import matplotlib.pyplot as plt
import pandas as pd

# constants for plot
det_num = int(input("Detector amount?: "))
plot_val = "MagnitudeofEnergyFlux"
maxlen = 8000

# plot all detector results
for i in range(1, det_num+1):
    file = f"detector_{i}_data.csv"

    df = pd.read_csv(file)
    plt.plot(df["TimeStep"][0:maxlen], df[plot_val][0:maxlen], marker="o", label=file[:-9])

# mark legend
plt.legend(loc="upper right")

# label axes
plt.xlabel("TimeStep(Frames)")
plt.ylabel(plot_val)

# show plot
plt.show()