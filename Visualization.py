import pandas as pd
import numpy as np
import plotly.graph_objects as go

def avg_normalize_data(dataframe, cols):
    cols_to_keep = cols + ['playlist']
#     avged_data = [df[cols_to_keep].groupby('playlist').mean() for df in data_arr]
#     master_df = pd.DataFrame().append(avged_data)
    master_df = dataframe[cols_to_keep].groupby('playlist').mean()
    for col in master_df.columns[1:]:
        norm = np.linalg.norm(master_df[col])
        master_df[col] = master_df[col]/norm
    return master_df

def make_radar_chart(data_arr, cols = ['danceability', 'energy', 'speechiness',
       'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']):
    master_df = avg_normalize_data(data_arr, cols)
    fig = go.Figure()
    categories = master_df.columns
    for idx, row in master_df.iterrows():
        #print(row)
        normal_array = row
        fig.add_trace(go.Scatterpolar(
              r=normal_array,
              theta=categories,
              fill='toself',
              name= str(idx)
        ))
        print("Added to figure")

    fig.update_layout(
      polar=dict(
        radialaxis=dict(
          visible=True,
          range=[0, 1]
        )),
      showlegend=True
    )

    return fig