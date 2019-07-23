from gensim.models.coherencemodel import CoherenceModel
from gensim.corpora.dictionary import Dictionary
from gensim.sklearn_api import LdaTransformer
from skopt import dump
from skopt import gp_minimize
from skopt.space import Real, Integer
from skopt import callbacks
from skopt.callbacks import CheckpointSaver
from skopt.utils import use_named_args
import csv
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import pandas as pd
import logging

logging.basicConfig(filename='/home/norberteke/PycharmProjects/Thesis/logs/model_selection.log', format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def createDictionary(texts):
    dictionary = Dictionary(texts)
    dictionary.filter_extremes(no_below=2, no_above=0.4, keep_n=1000000)
    dictionary.compactify()
    return dictionary

def saveModelConfigs(model, coherence, path):
    with open(path, 'a') as f:
        writer = csv.writer(f, delimiter = ',', quotechar='"', quoting = csv.QUOTE_MINIMAL)
        writer.writerow([str(model.num_topics), str(model.eta), str(coherence)])

def run_optimizer_SO_recent(runs, config_path):
    engine = create_engine("mysql+pymysql://norberteke:Eepaiz3h@localhost/norberteke")
    conn = engine.connect()

    activity_SQL = "SELECT full_activity FROM SO_recent_activity"
    data = pd.read_sql_query(sql=text(activity_SQL), con=conn)

    texts = []
    for line in data['full_activity']:
        if len(line.split()) < 1:
            texts.append([""])
        else:
            texts.append(line.split())

    def evaluateModel(model):
        cm = CoherenceModel(model=model, texts=texts, coherence='c_v')
        coherence = cm.get_coherence()  # get coherence value
        return coherence

    dictionary = createDictionary(texts)
    dictionary.save("/home/norberteke/PycharmProjects/Thesis/data/SO_recent_full_activity_gensimDictionary.dict")

    corpus = [dictionary.doc2bow(text) for text in texts]
    # output_fname = get_tmpfile("/home/norberteke/PycharmProjects/Thesis/data/SO_recent_full_activity_gensimCorpus.mm")
    # MmCorpus.serialize(output_fname, corpus)

    model = LdaTransformer(id2word=dictionary, alpha='auto', iterations=50, random_state=2019)

    # The list of hyper-parameters we want to optimize. For each one we define the bounds,
    # the corresponding scikit-learn parameter name
    space = [Integer(10, 1000, name='num_topics'), Real(0.001, 200, name='eta')]

    # this decorator allows your objective function to receive a the parameters as keyword arguments.
    # This is particularly convenient when you want to set scikit-learn estimator parameters
    @use_named_args(space)
    def objective(**params):
        model.set_params(**params)
        lda = model.fit(corpus)
        coherence = evaluateModel(lda.gensim_model)
        return 1 - coherence  # to maximize coherence score, minimize 1 - coherence score


    checkpoint_saver = CheckpointSaver("/home/norberteke/PycharmProjects/Thesis/data/SO_recent_param_optimizer_checkpoint.pkl", compress=9)  # keyword arguments will be passed to `skopt.dump`
    res_gp = gp_minimize(objective, space, n_calls=runs, callback=[checkpoint_saver], random_state=2019, verbose = True)

    try:
        dump(res_gp, '/home/norberteke/PycharmProjects/Thesis/data/SO_recent_param_optimizer_result_n1000.pkl')
    except:
        dump(res_gp,
             '/home/norberteke/PycharmProjects/Thesis/data/SO_recent_param_optimizer_result_without_objective_n1000.pkl',
             store_objective=False)
    finally:
        try:
            print("Best score=%.6f" % (1 - res_gp.fun))  # to make up for 1 - coherence (reverse the equation)

            print("""Best parameters:
            - num_topics=%d
            - eta=%.6f""" % (res_gp.x[0], res_gp.x[1]))
        except:
            print("Problems occured")
            print(str(res_gp.fun))
            print(str(res_gp.x[0]), str(res_gp.x[1]))

    from skopt.plots import plot_convergence
    plot_convergence(res_gp)


def run_optimizer_SO_past(runs, config_path):
    engine = create_engine("mysql+pymysql://norberteke:Eepaiz3h@localhost/norberteke")
    conn = engine.connect()

    activity_SQL = "SELECT full_activity FROM SO_past_activity"
    data = pd.read_sql_query(sql=text(activity_SQL), con=conn)

    texts = []
    for line in data['full_activity']:
        if len(line.split()) < 1:
            texts.append([""])
        else:
            texts.append(line.split())

    def evaluateModel(model):
        cm = CoherenceModel(model=model, texts=texts, coherence='c_v')
        coherence = cm.get_coherence()  # get coherence value
        return coherence

    dictionary = createDictionary(texts)
    dictionary.save("/home/norberteke/PycharmProjects/Thesis/data/SO_past_full_activity_gensimDictionary.dict")

    corpus = [dictionary.doc2bow(text) for text in texts]
    # output_fname = get_tmpfile("/home/norberteke/PycharmProjects/Thesis/data/SO_recent_full_activity_gensimCorpus.mm")
    # MmCorpus.serialize(output_fname, corpus)

    model = LdaTransformer(id2word=dictionary, alpha='auto', iterations=50, random_state=2019)

    # The list of hyper-parameters we want to optimize. For each one we define the bounds,
    # the corresponding scikit-learn parameter name
    space = [Integer(3, 1000, name='num_topics'), Real(0.001, 200, name='eta')]

    # this decorator allows your objective function to receive a the parameters as keyword arguments.
    # This is particularly convenient when you want to set scikit-learn estimator parameters
    @use_named_args(space)
    def objective(**params):
        model.set_params(**params)
        lda = model.fit(corpus)
        coherence = evaluateModel(lda.gensim_model)
        saveModelConfigs(lda, coherence, config_path)
        return 1 - coherence  # to maximize coherence score, minimize 1 - coherence score


    checkpoint_saver = CheckpointSaver("/home/norberteke/PycharmProjects/Thesis/data/SO_past_param_optimizer_checkpoint.pkl", compress=9)
    res_gp = gp_minimize(func=objective, dimensions=space, n_calls=runs, callback=[checkpoint_saver], random_state=2019, verbose=True)


    try:
        dump(res_gp, '/home/norberteke/PycharmProjects/Thesis/data/SO_past_param_optimizer_result_n' + str(runs) + '.pkl')
    except:
        dump(res_gp,
             '/home/norberteke/PycharmProjects/Thesis/data/SO_past_param_optimizer_result_without_objective_n' + str(runs) + '.pkl', store_objective=False)
    finally:
        try:
            print("Best score=%.6f" % (1 - res_gp.fun))  # to make up for 1 - coherence (reverse the equation)

            print("""Best parameters:
            - num_topics=%d
            - eta=%.6f""" % (res_gp.x[0], res_gp.x[1]))
        except:
            print("Problems occured")
            print(str(res_gp.fun))
            print(str(res_gp.x[0]), str(res_gp.x[1]))

    from skopt.plots import plot_convergence
    plot_convergence(res_gp)

if __name__ == '__main__':
    config_path = "/home/norberteke/PycharmProjects/Thesis/data/SO_past_model_parameter_config_log.csv"
    run_optimizer_SO_past(10, config_path)