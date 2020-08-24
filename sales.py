import pandas as pd
import numpy as np
import json
import os

from flask import Flask, request, jsonify
from flask_cors import CORS

#Web Scraping
from page import Page

app = Flask(__name__)
cors = CORS(app)

@app.route('/v1/correlacao', methods=['POST'])
def product_corrs():
    content = request.json
    dataset = pd.DataFrame(content['sales'])
    
    # agrupamento de descricao por id
    descricao_por_id = dataset.groupby('CustomerID')['StockCode'].value_counts()
    # gera distribuicao
    descricao_por_id = descricao_por_id.unstack().fillna(0)
    # filtra os campos principais
    descricao_por_id = pd.DataFrame(data = descricao_por_id.values, columns=descricao_por_id.columns.values.tolist(), index=descricao_por_id.index)
    # processa a correlacao dos dados
    corr_descricao_por_id = descricao_por_id.corr()
    # transforma em lista a correlacao processada
    maiores_corrs = corr_descricao_por_id.unstack().sort_values(ascending=False)[:]
    # elimina os duplicados
    maiores_corrs = maiores_corrs.drop_duplicates()
    # elimina as correlacoes com baixa porcentagem
    maiores_corrs = maiores_corrs.where(lambda x : x.values > 0.50).dropna()

    # Gerando a arvore de correlacoes 
    df_final = pd.DataFrame()
    grupo = ""
    series = pd.Series()
    serie = pd.Series()

    for i in maiores_corrs.index:
        grupo = i[0]

        if grupo in series:
            series[grupo].append(i[1])        
        else:
            serie = []
            serie.append(i[1])
            series[grupo] = serie        
    
    return series.to_json()


@app.route('/')
def status():
    return "...status ok..."

@app.route('/v1/search/<site>/<chave>')
def pages(site, chave):    
    return Page(site, chave).get_result()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)