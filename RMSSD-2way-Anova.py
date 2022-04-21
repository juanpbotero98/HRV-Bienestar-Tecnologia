from importlib.resources import path
import pandas as pd 
import os
import matplotlib.pyplot as plt
import seaborn as sns 
import pingouin as pg


# Load the data
path = os.path.join(os.getcwd(),'RMSSD-2way-ANOVA.csv')
df = pd.read_csv(path)
print(df.head(2))
# Create a boxplot
sns.boxplot(x="Seccion",y="RMSSD",hue= "Experiencia",data=df, palette="Set3")
plt.show()
# Summarize the data statistics
res = pg.rm_anova(data=df, dv="RMSSD", within=["Seccion","Experiencia"], subject="Sujetos",detailed=True)
print(res)