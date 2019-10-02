#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 15:16:44 2019

@author: tarik
"""



# librairies de manipulation des données
import pandas as pd

# librairies pour concevoir et faire fonctionner l'application
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

# librairies de visualisation (table + graph)
import dash_table
#from dash_table import DataTable
import plotly.graph_objs as go

#Import des données----------------------------------------------------------------------------------------------------------------------

import numpy as np
import sqlalchemy as db
from sqlalchemy import create_engine
import argparse
#~ import creds
import os,configparser 
#création d'un Fichier 
parser = argparse.ArgumentParser()
#~ parser.add_argument("-f", action="store_true", help="traite Film")
#~ parser.add_argument("-p", action="store_true", help="traite People")

parser.add_argument("--base", help="Répertoire de movies")
parser.add_argument("--bdd", help="Base de donnée")
args = parser.parse_args()

config = configparser.ConfigParser()
config.read_file(open(os.path.expanduser("~/.datalab.cnf")))
print(config.sections())

base = args.base # "/home/tarik/Documents/BDD_Mysql/movies-master/data"


mySQLengine = create_engine("mysql://%s:%s@%s/%s" % (config['myBDD']['user'], config['myBDD']['password'], config['myBDD']['host'], 'BDD_Tarik'))


connection = mySQLengine.connect()
metadata = db.MetaData()
FILMetREMAKE = db.Table('FILMetREMAKE', metadata, autoload=True, autoload_with=mySQLengine)


#Equivalent to 'SELECT * FROM census'
query = db.select([FILMetREMAKE])

ResultProxy = connection.execute(query)

ResultSet = ResultProxy.fetchall()


df = pd.DataFrame(ResultSet)
df.columns = ResultSet[0].keys()

print(df)

# CREATION DE L'APPLICATION ----------------------------------------------------------------------------------------------------------
app = dash.Dash()

app.layout = html.Div(children=[
            # Titre de l'application    
    html.H1(
        children="BGT Médiathèque ",
        style={'textAlign': 'center'}
    ),

    # Un slider permettant de selectionner les années des films
    html.Br(),
    html.Hr(),
    html.Label('Sélection par Années', style={'fontSize': 20, 'marginTop': 30}),
    dcc.RangeSlider(
        id='input-year',
        min=1891,
        max=2001,
        step=50,
        marks={i: format(i) for i in range(1891, 2001)},
        
    # pour les valeurs par défaut, intégration dynamique des valeurs min et max de la table de données 
        value=[df['Annee'].min(), df['Annee'].max()], 
    ),
    html.Br(),
    html.Br(),
    html.Div(id='output-year'),
    
    # Une zone de sélection pour choisir le/les films souhaitees
    html.H4(
        children='Liste des Films dispo'),
    dcc.Dropdown(id='dropdown', options=[
        {'label': i, 'value': i} for i in df.Titre_filmetRemake.unique()
    ], multi=True, placeholder='Filter by title...'),
    html.Div(id='table-container'
    ),

             
    # Affichage de la table ainsi qu'un peu d'habillage
    html.Br(),
    html.Hr(),
    html.Label('Table de Films', style={'fontSize': 20, 'marginTop': 30}),
    html.Div(id='output-data'),
    


])



# Données Year-------------------------------------------------------------------------------------------------------------
@app.callback(Output('output-year', 'children'), # LIRE : "ma sortie à modifier est 'output-year' (identifiant de la 'Div html') et concerne la propriété 'children'
              [Input('input-year', 'value')]) # LIRE : "mon entrée à utiliser est 'input-atmo' (identifiant du SliderRange) et concerne la propriété 'value'
def update_year(input):
    return u'Vous avez sélectionné les Annees : {}'.format(input)

# Données Titre-------------------------------------------------------------------------------------------------------------

@app.callback(
    dash.dependencies.Output('table-container', 'children'),
    [dash.dependencies.Input('dropdown', 'value')])

def display_titre(dropdown_value):
    
    return u'Vous avez sélectionné le(s) Film(s) : {}'.format(dropdown_value)
 

# Table-------------------------------------------------------------------------------------------------------------------------
@app.callback(Output('output-data', 'children'),
              [Input('input-year', 'value'),
               Input('dropdown', 'value')]) # LIRE : "la première variable de la fonction concerne la première entrée (INPUT) déclarée dans le app.callback, et ainsi de suite pour les autres variables (on respecte l'ordre de déclaration)

def update_table(year, Titre):
    #print(Titre)
    if Titre is None:
      dff=df[(df['Annee'] >= year[0]) & (df['Annee'] <= year[1])]
    else :
    # Création d'une nouvelle dataframe (dff) qui est la mise à jour de la dataframe initiale (df) selon les paramètres utilisateurs
     dff = df[(df['Annee'] >= year[0]) & (df['Annee'] <= year[1])& (df['Titre_filmetRemake'].isin(Titre))]
    
    table = html.Div([
            dash_table.DataTable(
                data=dff.to_dict('rows'),
                columns=[{'name': i, 'id': i} for i in dff.columns],
                editable=False,
                filtering=False,
                sorting=True,
                sorting_type="multi",
                row_selectable="multi",
                row_deletable=False,
                pagination_mode="fe",
                pagination_settings={
                        "current_page": 0,
                        "page_size": 20}
                )
            ])
    return table







# LANCEMENT DE L'APPLICATION --------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
    

                    