
import os
import sys
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import psycopg2
import pandas as pd
import numpy as np

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def open_connection_to_db():
    print('open_connection_to_db ')    
    try:
         conn  = psycopg2.connect(database = os.environ['db_name'], 
                                  host     = os.environ['db_host'], 
                                  user     = os.environ['db_user_name'], 
                                  password = os.environ['db_password'], 
                                  port     = os.environ['db_port'])    
         autocommit = True
         if (autocommit):
             conn.autocommit = True
         cursor = conn.cursor()
         print      ('open_connection_to_db success ') 
    except:
        print      ('open_connection_to_db: ERROR ') 
    return conn, cursor

def get_most_recent_values_by_single_userid(conn,cursor,userid):
    #sql_statement = """SELECT userid, dt_last, lon_last, lat_last, total_dist FROM leaderboard WHERE userid = '%s'""" % (userid)
    sql_statement = """SELECT userid, dt_last, total_dist \
        FROM checkpoints WHERE userid = '%s' \
        ORDER BY dt_last DESC \
        LIMIT 1""" % (int(userid))
    # n = 33753
    # sql_statement = """SELECT userid, dt_last, lon_last, lat_last, total_dist FROM leaderboard WHERE userid = '%s'""" % (n)
    # cursor.execute(sql_statement)
    # results = cursor.fetchall()
    # print(results)
    #sql_statement = """SELECT userid, dt_last, lon_last, lat_last, total_dist 
    #                           FROM leaderboard 
    #                           ORDER BY total_dist DESC
    #                           LIMIT 10"""
    cursor.execute(sql_statement)
    user_most_recent_checkpoint = cursor.fetchall()[0]
    #print(leaders_df.head())
    return user_most_recent_checkpoint

def get_checkpoints_by_single_userid(conn,cursor,userid):
    sql_statement = """SELECT userid, dt_last, segment_dist, total_dist FROM checkpoints WHERE userid = '%s'""" % (int(userid))
    user_checkpoint_df = pd.read_sql(sql_statement,conn)
    #print(user_checkpoint_df.head())
    #user_last_checkpoint = user_checkpoint_df.iloc[0]['userid']
    #if (batch_df['id'][n] == 1):
    #    print('    found checkpoint user %s dt %5.1f lon %5.1f lat %5.1f  segment_dist %5.1f ' %(user_checkpoint_df.iloc[-1]['userid'], user_checkpoint_df.iloc[-1]['dt_last'], user_checkpoint_df.iloc[-1]['lon_last'], user_checkpoint_df.iloc[-1]['lat_last'], user_checkpoint_df.iloc[-1]['segment_dist']))
    return user_checkpoint_df

def get_current_leaderboard(conn,cursor):
    sql_statement = """SELECT userid, dt_last, segment_dist, total_dist \
        FROM checkpoints \
        WHERE total_dist IS NOT NULL \
        AND segment_dist < 2.0 \
        ORDER BY total_dist DESC \
        LIMIT 20""" 
    leaderboard_df = pd.read_sql(sql_statement,conn)
    #leaderboard_df.drop('segment_dist', axis=1, inplace=True)
    #leaderboard_df['userid'] = leaderboard_df['userid'].map("{:,.0f}".format)
    leaderboard_df['userid']  = leaderboard_df['userid'].map("{:.0f}".format)
    leaderboard_df['dt_last'] = leaderboard_df['dt_last'].map("{:.1f}".format)
    leaderboard_df['segment_dist'] = leaderboard_df['segment_dist'].map("{:.2f}".format)
    leaderboard_df['total_dist'] = leaderboard_df['total_dist'].map("{:.2f}".format)
    #leaderboard_df.head(50)
    return leaderboard_df

def generate_table(leaderboard_df, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in leaderboard_df.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(leaderboard_df.iloc[i][col]) for col in leaderboard_df.columns
            ]) for i in range(min(len(leaderboard_df), max_rows))
        ])
    ])



(conn,cursor) = open_connection_to_db()

userid = 1
(user_checkpoint_df) = get_checkpoints_by_single_userid(conn,cursor,userid)
#print(user_checkpoint_df.head(20))

(leaderboard_df) = get_current_leaderboard(conn,cursor)
#leaderboard_df.columns = ['userid', 'last reported time', 'distance_traveled']
leaderboard_df.columns = ['userid', 'last report [min]', 'last segment distance [km]', 'total distance [km]']
print(leaderboard_df.head(40))

(user_most_recent_checkpoint) = get_most_recent_values_by_single_userid(conn,cursor,userid)
#print(user_most_recent_checkpoint)









#    html.H1(children='RaceCast: Live Race Leaderboard'),
#app.layout = html.Div(children=[
app.layout = html.Div([
    html.Div(html.H1('RaceCast: Live Race Leaderboard'), style={'textAlign': 'center'}),
    html.Div(generate_table(leaderboard_df), style={'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
    #html.Div(id='div_figure1', style={'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
    html.Div(html.H2('Leaderboard Progress vs Time'), style={'margin-top': '10px', 'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
    html.Div(id='div_figure1', style={'margin-top': '20px', 'width': '100%', 'align-items': 'center', 'justify-content': 'center'}),

    html.Div(html.H2('To track progress on an athlete, enter their ID'), style={'margin-top': '10px', 'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),

    #html.Div(dcc.Input(id='div_user_id_text_box1', value='1', type='text')),
    html.Div(dcc.Input(id='div_user_id_text_box2', value='1',type='text'), style={'margin-top': '10px', 'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
    html.Div(html.Button('Submit', id='submit-val', n_clicks=0), style={'margin-top': '10px', 'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
    html.Div(id='container-button-basic',children='Enter a value and press submit'),
    html.Div(id='div_display-userid'),
    html.Div(id='div_figure2'),
    #dcc.Graph(id='graph1')
])


#@app.callback(
#    dash.dependencies.Output('container-button-basic', 'children'),
#    [dash.dependencies.Input('submit-val', 'n_clicks')],
#    [dash.dependencies.State('div_user_id_text_box2', 'value')])
#def update_output(n_clicks, value):
#    return 'User selected is "{}" '.format(value)

@app.callback(
    Output('div_display-userid', 'children'),
    [Input('div_user_id_text_box2',  'value')]
)
def update_output_div(input_value):
    return 'User selected is {}'.format(input_value)

@app.callback(
    Output(component_id='div_figure1',component_property='children'),
    [Input(component_id='div_user_id_text_box2',component_property='value')]    
)
def update_graph1(div_user_id_text_box2):
    leaderboard_df = get_current_leaderboard(conn, cursor)
    #print(leaderboard_df.head(20))    
    leaders_ids = leaderboard_df['userid']
    n_leaders = len(leaders_ids)
    for n in range(0, n_leaders, 1):
        (user_checkpoint_df) = get_checkpoints_by_single_userid(conn,cursor,leaders_ids[n])
        #print(user_checkpoint_df.head(20))
        if   (n == 0):
            df_temp0 = user_checkpoint_df
        elif (n == 1):
            df_temp1 = user_checkpoint_df
        elif (n == 2):
            df_temp2 = user_checkpoint_df
        elif (n == 3):
            df_temp3 = user_checkpoint_df
    return dcc.Graph(
        figure=dict(
            data=[
                dict(
                    x=df_temp0['dt_last'],
                    y=df_temp0['total_dist'],
                    name=leaders_ids[0],
                    marker=dict(color='rgb(55, 83, 109)')),
                dict(
                    x=df_temp1['dt_last'],
                    y=df_temp1['total_dist'],
                    name=leaders_ids[1],
                    marker=dict(color='rgb(15, 100, 100)')),
                dict(
                    x=df_temp2['dt_last'],
                    y=df_temp2['total_dist'],
                    name=leaders_ids[2],
                    marker=dict(color='rgb(80, 20, 30)')),
                dict(
                    x=df_temp3['dt_last'],
                    y=df_temp3['total_dist'],
                    name=leaders_ids[3],
                    marker=dict(color='rgb(55, 109, 10)')),
            ],
            layout=dict(
                title='Leaderboard Progress vs Time ',
                xaxis={'title': 'elapsed time [s]',
                       'type': 'linear',
                       'range': [0, 10]
                      },
                yaxis={'title': 'distance traveled',
                       'type': 'linear', 
                       'range': [0, 30]
                      },
                showlegend=True,
                legend=dict(
                    x=0,
                    y=1.0
                ),
                margin=dict(l=40, r=0, t=40, b=30)
            )
        ),
        style={'height': 300},
    )

#@app.callback(
#    Output(component_id='div_figure2',component_property='children'),
#    [Input(component_id='div_user_id_text_box',component_property='value')]    
#)

n_clicks = 10
@app.callback(
    dash.dependencies.Output('container-button-basic', 'children'),
    [dash.dependencies.Input('submit-val', 'n_clicks')],
    [dash.dependencies.State('div_user_id_text_box2', 'value')])
def update_graph2(n_clicks, div_user_id_text_box2):
    (user_checkpoint_df) = get_checkpoints_by_single_userid(conn,cursor,div_user_id_text_box2)
    #print(user_checkpoint_df.head())
    return dcc.Graph(
        figure=dict(
            data=[
                dict(
                    x=user_checkpoint_df['dt_last'],
                    y=user_checkpoint_df['total_dist'],
                    name=div_user_id_text_box2,
                    marker=dict(color='rgb(55, 83, 109)'))
            ],
            layout=dict(
                title='User '+str(div_user_id_text_box2)+' distance vs time   ',
                xaxis={'title': 'elapsed time [s]',
                       'type': 'linear',
                       'range': [0, 10]
                      },
                yaxis={'title': 'distance traveled',
                       'type': 'linear', 
                       'range': [0, 30]
                      },
                #x='x Axis Title',
                #xaxis=dict('title':'title_text',  range:(0,10,1)),
                #y='y Axis Title',
                #yaxis={'range': range(0,10,1)},
                showlegend=True,
                legend=dict(x=0,y=1.0),
                margin=dict(l=40, r=0, t=60, b=60)
                )    
            ),
        style={'height': 400},
    )

# ec2
if __name__ == '__main__':
    app.run_server(debug=True)
    #app.run_server(debug=True, port=8050, host='ec2-34-222-54-126.us-west-2.compute.amazonaws.com')


# ec2-34-222-54-126.us-west-2.compute.amazonaws.com:8050

# local
#if __name__ == '__main__':



#app.layout = html.Div([
#])



# @app.callback(
#     Output('div_figure1', 'figure'),
#     [Input('div_user_id_text_box2', 'value')])
# def update_figure(selected_year):
#     return {

#         'data': traces,
#         'layout': dict(
#             xaxis={'type': 'log', 'title': 'GDP Per Capita',
#                    'range':[2.3, 4.8]},
#             yaxis={'title': 'Life Expectancy', 'range': [20, 90]},
#             margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
#             legend={'x': 0, 'y': 1},
#             hovermode='closest',
#             transition = {'duration': 500},
#         )
        
        

#         dcc.Graph(
#             figure=dict(
#                 data=[
#                     dict(
#                         x=[1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003,
#                            2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012],
#                         y=[219, 146, 112, 127, 124, 180, 236, 207, 236, 263,
#                            350, 430, 474, 526, 488, 537, 500, 439],
#                         name='Rest of world',
#                         marker=dict(
#                             color='rgb(55, 83, 109)'
#                         )
#                     ),
#                     dict(
#                         x=[1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003,
#                            2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012],
#                         y=[16, 13, 10, 11, 28, 37, 43, 55, 56, 88, 105, 156, 270,
#                            299, 340, 403, 549, 499],
#                         name='China',
#                         marker=dict(
#                             color='rgb(26, 118, 255)'
#                         )
#                     )
#                 ],
#                 layout=dict(
#                     title='US Export of Plastic Scrap',
#                     showlegend=True,
#                     legend=dict(
#                         x=0,
#                         y=1.0
#                     ),
#                     margin=dict(l=40, r=0, t=40, b=30)
#                 )
#             )
#             )
#         }





######################################
# auto refresh 

#dcc.Interval(
#    id='interval-component',
#    interval=1*1000, # in milliseconds
#    n_interval=0)
# app.layout = html.Div(
#     [
#     html.H4('Stock_Data_Streaming'),
#     dcc.Graph(id='live-graph', animate=True), 
#     dcc.Interval(
#         id='graph-update',
#         interval=1*100,
#         n_intervals=0
#     )
#     ]
# )
#app.layout = html.Div(
#    html.Div([
#        html.H4('TERRA Satellite Live Feed'),
#        html.Div(id='live-update-text'),
#        dcc.Graph(id='live-update-graph'),
#        dcc.Interval(
#            id='interval-component',
#            interval=1*1000, # in milliseconds
#            n_intervals=0
#        )
#    ])
#)

# auto refresh 
######################################







#@app.callback(
#    [Output(component_id='graph1', component_property='figure')],
#    [Input (component_id='user_id_text_box', component_property='value')])

#@app.callback(
#    Output('barplot-topactivity', 'figure'),
#    [Input('activity', 'value'),
#    Input('slider_updatetime', 'value')])
#def update_graph(activity, slider_updatetime):


#@app.callback(
#     Output('graph1', 'figure'),
#     [Input('user_id_text_box', 'value')
#     ]
# )

# def update_graph(user_id_text_box):
#     (results) = get_values_by_userid(conn,cursor,userid)
#     print(results)
#     cursor = connection.cursor()
#     table_name = activity + 'event_table'
#     start_time = getSliderTime(slider_updatetime)
#     y_label = "label"
#     if activity == 'aggregate':
#         y_label = "aggregate score"
#         cursor.execute("select repo_name, sum(score)  from {} where create_date >= \'{}\' group by repo_name ORDER BY sum(score) desc LIMIT 20".format(table_name, start_time))
#     else:
#         y_label = "no. of " + activity.lower() + " events"
#         y_label = "no. of " + activity.lower() + " events"
#         cursor.execute("select repo_name, sum(count)  from {} where create_date >= \'{}\' group by repo_name ORDER BY sum(count) desc LIMIT 20".format(table_name, start_time))
#     data = cursor.fetchall()
#     repo_list = []
#     count_list = []
#     for i in range(len(data)):
#         repo_list.append(data[i][0])
#         count_list.append(data[i][1])
#     return {
#         'data': [go.Bar(
#             x=repo_list,
#             y=count_list,
#             opacity= 0.5,
#             marker={'color':'#800080'}
#         )],
#         'layout': go.Layout(
#             yaxis={'title': '{}'.format(y_label)},
#             legend={'x': 0, 'y': 1},
#             hovermode='closest',
#             plot_bgcolor='rgb(240,248,255)'
#         )
#     }




#''' This functions converts a dataframe into an HTML table '''
# def generate_table2(leaderboard_df, max_rows=10):
#     return html.Table(
#         # Header
#         [html.Tr([html.Th(col) for col in leaderboard_df.columns])] +

#         # Body
#         [html.Tr([
#             html.Td(html.A(str(int(leaderboard_df.iloc[i][col])), href='https://stackoverflow.com/questions/'+str(int(leaderboard_df.iloc[i][col])))) for col in leaderboard_df.columns
#         ]) for i in range(min(len(leaderboard_df), max_rows))]
#     )






# top_tags = ['java','python','scala','javascript','c','git'] # top 7 tags to be chosen as input

# app.layout = html.Div([
# 	
# 	# This div contains the header
# 	html.Div([ html.H1(children='Spam Stack')
#                ], className= 'twelve columns', style={'textAlign':'center'}) ,

# 	# This div contains a dropdown to record the user input
#     html.Div([ dcc.Dropdown( id = 'input-tag',
#                              options = [{ 'label': val , 'value': val} for val in top_tags],
#                              value='java')

#     ]),

#     # This div contains a scatter plot which comapres the scores of posts and the table with posts that need most cleaning
#     html.Div([
#             html.Div([dcc.Graph(id='g1')],className='ten columns'),
#             html.Div([html.Div(id='table-container',)] 
#              , className='two columns'),
            
#     ]),

# ])

# @app.callback(
#     [Output(component_id='g1', component_property='figure'),
#     Output(component_id='table-container', component_property='children')],
#     [Input(component_id='input-tag', component_property='value')])
    
# def make_query(input_tag):
#     custom_query_1 = " SELECT  *  from " + input_tag + "_avg_score order by "+ input_tag +"_avg_score.\"_ParentId\"  LIMIT 1000; "
#     df1 = load_data(custom_query_1)
#     custom_query_2 = " SELECT * from " + input_tag + "_avg_new LIMIT 1000;"
#     df2 = load_data(custom_query_2)
#     custom_query_3 = " SELECT "+ input_tag +"_improv.\"_ParentId\" as \"Posts\" from " + input_tag + "_improv LIMIT 7;"
#     df3 = load_data(custom_query_3)
#     data_table = generate_table(df3)
#     return [{'data': [{'x': df1['_ParentId'], 'y': df1['_avgscore'],'mode':'markers', 'name':'Before'},
#                       {'x': df2['_ParentId'], 'y': df2['_avgscore'],'mode':'markers','opacity':0.7,'name':'After'}],
#          	'layout': {'xaxis': {'title': 'Post Id'}, 'yaxis': {'title': 'Score'}}},
#          	data_table]
 
# colors = {
#     'background': '#111111',
#     'text': '#7FDBFF'
# }

# app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
#     html.H1(
#         children='Hello Dash',
#         style={
#             'textAlign': 'center',
#             'color': colors['text']
#         }
#     ),

#     html.Div(children='Dash: A web application framework for Python.', style={
#         'textAlign': 'center',
#         'color': colors['text']
#     }),

#     dcc.Graph(
#         id='example-graph-2',
#         figure={
#             'data': [
#                 {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
#                 {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
#             ],
#             'layout': {
#                 'plot_bgcolor': colors['background'],
#                 'paper_bgcolor': colors['background'],
#                 'font': {
#                     'color': colors['text']
#                 }
#             }
#         }
#     )
# ])


#if __name__ == '__main__':
#    app.run_server(debug=True,host="0.0.0.0",port=80)

    
    
#FROM checkpoints \
#     ORDER BY userid,total_dist DESC"""
# sql_statement = """SELECT DISTINCT ON (userid) userid, dt_last, total_dist \
#     FROM checkpoints \
#     ORDER BY userid DESC""" 

# # no
# sql_statement = """SELECT DISTINCT ON (userid) userid, dt_last, total_dist \
#     FROM checkpoints \
#     ORDER BY userid,total_dist DESC""" 

# # no
# sql_statement = """SELECT DISTINCT ON (userid) userid, dt_last, total_dist \
#     FROM checkpoints \
#     ORDER BY total_dist,userid DESC""" 

# # does not work 
# sql_statement = """SELECT DISTINCT ON (userid) userid, dt_last, total_dist \
#     FROM checkpoints \
#     ORDER BY userid DESC
#     ORDER BY total_dist DESC""" 


# sql_statement = """SELECT DISTINCT ON (total_dist) userid, dt_last, total_dist \
#     FROM checkpoints \
#     ORDER BY total_dist DESC""" 

# sql_statement = """SELECT DISTINCT ON (total_dist) userid, dt_last, total_dist \
#     FROM checkpoints \
#     ORDER BY total_dist,userid ASC""" 



# # 1
# sql_statement = """SELECT DISTINCT ON (total_dist,userid) userid, dt_last, total_dist \
#     FROM checkpoints \
#     ORDER BY total_dist,userid ASC""" 
# checkpoints_df = pd.read_sql(sql_statement,conn)
# checkpoints_df.head(20)

# # 2
# sql_statement = """SELECT DISTINCT ON (total_dist,userid) userid, dt_last, total_dist \
#     FROM checkpoints \
#     ORDER BY total_dist,userid DESC""" 
# checkpoints_df = pd.read_sql(sql_statement,conn)
# checkpoints_df.head(20)

# # 3
# sql_statement = """SELECT DISTINCT ON (total_dist,userid) userid, dt_last, total_dist \
#     FROM checkpoints \
#     ORDER BY userid,total_dist ASC""" 
# checkpoints_df = pd.read_sql(sql_statement,conn)
# checkpoints_df.head(20)

# # 4
# sql_statement = """SELECT DISTINCT ON (total_dist,userid) userid, dt_last, total_dist \
#     FROM checkpoints \
#     ORDER BY userid,total_dist DESC""" 
# checkpoints_df = pd.read_sql(sql_statement,conn)
# checkpoints_df.head(20)


# sql_statement = """SELECT DISTINCT ON (userid,total_dist) userid, dt_last, total_dist \
#     FROM checkpoints \
#     ORDER BY total_dist,userid ASC""" 
# checkpoints_df = pd.read_sql(sql_statement,conn)
# checkpoints_df.head(20)





# sql_statement = """SELECT userid, dt_last, total_dist \
#     FROM checkpoints \
#     ORDER BY total_dist DESC""" 
# checkpoints_df = pd.read_sql(sql_statement,conn)
# checkpoints_df.head(20)



# SELECT 
# first(COL1) over (partition by user_id order by COL2 rows unbounded following) 
# FROM table;


# sql_statement = """SELECT last(userid) |
#     OVER (PARTITION BY userid ORDER BY total_dist) \
#     FROM checkpoints""" 
# checkpoints_df = pd.read_sql(sql_statement,conn)
# checkpoints_df.head(20)


# sql_statement = """SELECT last(userid, dt_last, total_dist)
#     OVER (PARTITION BY userid ORDER BY total_dist) \
#     FROM checkpoints \
#     ORDER BY total_dist DESC""" 



# sql_statement = """SELECT userid, dt_last, lon_last, lat_last, segment_dist, total_dist FROM checkpoints ORDER BY userid"""
# checkpoints_df = pd.read_sql(sql_statement,conn)
# checkpoints_df.head(20)
# checkpoints_df.tail(20)




# sql_statement = """SELECT userid, dt_last, total_dist FROM checkpoints"""
# cursor.execute(sql_statement)
# results = cursor.fetchall()
# print(results)


# userid = 1


# sql_statement = """SELECT userid, dt_last, total_dist 
#     FROM checkpoints 
#     WHERE userid = 1
#     ORDER BY dt_last DESC
#     LIMIT 1"""




    
# cursor.execute(sql_statement)
# results = cursor.fetchall()
# print(results)





# #cursor.execute(sql_statement)
# #results = cursor.fetchall()
# #print(leaderboard_df.head())
# return leaderboard_df


# (leaderboard_df) = get_current_leaderboard(conn,cursor)
# leaderboard_df.head(20)


# (conn,cursor) = open_connection_to_db()

# userid = 1
# (most_recent_results_single_id) = get_most_recent_values_by_single_userid(conn,cursor,userid)
# print(most_recent_results_single_id)

# (user_checkpoint_df) = get_checkpoints_by_single_userid(conn,cursor,userid)
# print(user_checkpoint_df)
# user_checkpoint_df.head()


# sql_statement = """SELECT userid, dt_last, lon_last, lat_last, total_dist FROM leaderboard WHERE userid = '%s'""" % (n)
# sql_statement = """SELECT userid, dt_last, lon_last, lat_last, total_dist 
#sql_statement = """SELECT userid, dt_last, total_dist 
#                           FROM leaderboard 
#                           ORDER BY total_dist DESC
#                           LIMIT 10"""
#sql_statement = """SELECT userid, dt_last, total_dist 
#                           FROM leaderboard 
#                           ORDER BY total_dist DESC
#                           LIMIT 10"""
#sql_statement = """SELECT DISTINCT ON (userid) userid, dt_last, total_dist \
# 





    