from flask import Flask,render_template,request
import spacy
from spacy.matcher import Matcher 
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os
import time
nlp=spacy.load('en_core_web_sm')

def Findentities(sent):

    ent1 = ""
    ent2 = ""

    prv_tok_dep = ""    
    prv_tok_text = ""   

    prefix = ""
    modifier = ""
  
    for tok in nlp(sent):
#         print(tok.dep_,tok,'pre: '+prefix,"mod: "+modifier)
        if tok.dep_ != "punct":

            if tok.dep_ == "compound":
                prefix = tok.text

                if prv_tok_dep == "compound":
                    prefix = prv_tok_text + " "+ tok.text
      

            if tok.dep_.endswith("mod") == True:
                modifier = tok.text

                if prv_tok_dep == "compound":
                    modifier = prv_tok_text + " "+ tok.text
      

            if tok.dep_.find("subj") == True:
                ent1 = modifier +" "+ prefix + " "+ tok.text
                prefix = ""
                modifier = ""
                prv_tok_dep = ""
                prv_tok_text = ""      


        if tok.dep_.find("obj") == True:
            ent2 = modifier +" "+ prefix +" "+ tok.text
            modifier=""
            prefix=ent2

        prv_tok_dep = tok.dep_
        prv_tok_text = tok.text
#         print(prv_tok_dep,prv_tok_text)

    return [ent1.strip(), ent2.strip()]


def get_relation(sent):

    doc = nlp(sent)

  # Matcher class object 
    matcher = Matcher(nlp.vocab)

  #define the pattern 
    pattern = [{'DEP':'ROOT'}, 
            {'DEP':'prep','OP':"?"},  
            {'DEP':'agent','OP':"?"},  #agent
            {'POS':'ADJ','OP':"?"}]  #affix

    matcher.add("matching_1", None, pattern) 
    
    matches = matcher(doc)
    k = len(matches) - 1

    span = doc[matches[k][1]:matches[k][2]] 

    return(span.text)


app=Flask(__name__)
@app.route("/")
def nigga():
    return render_template("show.html")

@app.route("/",methods=["POST"])
def noice():
    data=request.form['Text1']
    split_data=data.split('\n')
    all_entities=[ Findentities(i) for i in split_data]
    print(all_entities)
    all_relations=[get_relation(i) for i in split_data]
    print(all_relations)
    source = [i[0] for i in all_entities]

    target = [i[1] for i in all_entities]

    kg_df = pd.DataFrame({'source':source, 'target':target, 'edge':all_relations})

    G=nx.from_pandas_edgelist(kg_df, "source", "target", edge_attr=True, create_using=nx.MultiDiGraph())
    plt.figure(figsize=(12,12))
    pos = nx.spring_layout(G)
    nx.draw(G, with_labels=True, node_color='skyblue', edge_cmap=plt.cm.Blues, pos = pos)


    new_graph_name = "graph" + str(int(time.time())) + ".png"
    for filename in os.listdir('static/'):
        if filename.startswith('graph_'):  # not to remove other images
            os.remove('static/' + filename)
    
    plt.savefig('./static/'+new_graph_name)
    return render_template('page2.html',url=new_graph_name)

if __name__ == "__main__":
    app.run()