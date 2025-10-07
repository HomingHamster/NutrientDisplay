import pandas as pd
df = pd.read_csv(input("enter fn: "))

unique_values = df[input("en col: ")].unique()
print(unique_values)
print(len(unique_values))

#en94compre28compl92