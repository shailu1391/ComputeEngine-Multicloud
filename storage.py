import pandas as pd

a = pd.read_csv("datahistory.csv")

a.to_html("output.html")