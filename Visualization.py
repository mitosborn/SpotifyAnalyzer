import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
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

def make_bar_graph(df):
    data = df[['year','playlist']].copy()
    data.rename(columns={'year': 'decade'}, inplace=True)
    data['count'] = 1
    data['decade'] = data['decade'].apply(lambda x: str(x)[:3] + '0s')
    data = data.groupby(['playlist','decade']).sum().reset_index()
    to_return = data.pivot(index = 'decade', columns = 'playlist',values = 'count')
    to_return = to_return.fillna(0).astype(int)
    to_return.reset_index(inplace = True)
    return px.bar(to_return,x='decade',y=to_return.columns[1:],barmode = 'group',labels={'decade':'Decade','value':'Frequency'})