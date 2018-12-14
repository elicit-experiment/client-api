import pandas as pd

parse_dates = {'time' : [1]}
dtypes = {
}
df = pd.read_table('video.csv', parse_dates=parse_dates, sep=',')

print(df.sort_values(by=['time']))