import pandas as pd 
import numpy as np 
from io import BytesIO
import xlsxwriter
import zipfile
import streamlit as st 

st.set_page_config(layout='wide')
st.title('Preparazione dati inventario')

# Calcolo solo i codici con pct cumulata a scelta
# 70, 80, 90%

layout = {
    'PF' : ['CLASSE','GRUPPO','ARTICOLO','DESCRIZIONE','ABC','UM','Cod. collocazione','Descrizione Collocazione'] ,
    'other' : ['CLASSE','GRUPPO','ARTICOLO','DESCRIZIONE','ABC','UM'] ,
    'merge' : ['Nr. articolo','Cod. collocazione','Descrizione Collocazione'],
}

def scarica_excel(df, filename):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1',index=False)
    writer.close()

    st.download_button(
        label="Download Excel workbook",
        data=output.getvalue(),
        file_name=filename,
        mime="application/vnd.ms-excel"
    )

path = st.file_uploader('Caricare il file "Valorizzazione Magazzino"')
if not path:
    st.stop()

path_ub = st.file_uploader('Caricare il file "Contenuto collocazioni"')
if not path_ub:
    st.stop()

df = pd.read_excel(path)
df_ub = pd.read_excel(path_ub)

df = df.sort_values(by='VALORE_TOT', ascending=False)
df['cum'] = df.VALORE_TOT.cumsum()
df['pct'] = df.cum / df.VALORE_TOT.sum()

#pct_limit = st.radio('Selezionare soglia% valore totale', options=['70%','80%','90%'])
#pct_dic = {
    #'70%' : 0.7 ,
    #'80%' : 0.8 ,
   # '90%' : 0.9
#}

df['ABC'] = np.where((df.pct <= 0.8), 'A', 'C')
df['ABC'] = np.where((df.pct > 0.8) & (df.pct <= 0.9), 'B', df['ABC'])

#df = df[df.pct<= pct_dic[pct_limit]]
df = df.merge(df_ub, how='left',left_on = 'ARTICOLO', right_on = 'Nr. articolo')
df = df.sort_values(by=['CLASSE','GRUPPO','ARTICOLO'])
df['chiave'] = np.where(df.CLASSE == 'PF','PF', df.CLASSE + ' | ' + df.GRUPPO)
#df['chiave'] = np.where(df.CLASSE == 'MP','MP',df.chiave)

count = df[['chiave','ARTICOLO']].groupby(by='chiave').count()
count = count.sort_values(by='ARTICOLO',ascending=False)

pf = df[df.chiave == 'PF']
other = df[df.chiave!= 'PF']



st.subheader(f'{len(df)} Codici da inventariare', divider = 'red')
st.subheader('Prodotto finito')
st.dataframe(pf[layout['PF']], width=2000)
st.write(f'{len(pf)} codici di prodotto finito da inventariare')
scarica_excel(pf[layout['PF']],'Prodotto finito da inventariare.xlsx')

st.subheader('Altro')
st.dataframe(other[layout['other']], width=2000)
st.write(f'{len(other)} codici da inventariare')
scarica_excel(other[layout['other']],'Codici non finiti da inventariare.xlsx')
