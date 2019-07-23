from sqlalchemy import create_engine
from sqlalchemy.sql import text
import text_processing
import pandas as pd
import logging
logging.basicConfig(filename='/home/norberteke/PycharmProjects/Thesis/logs/GH_clean_aggregate.log', format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

exceptions_filename_past = '/home/norberteke/PycharmProjects/Thesis/data_cleaning/GH_past_exceptions_list.txt'
exceptions_filename_recent = '/home/norberteke/PycharmProjects/Thesis/data_cleaning/GH_recent_exceptions_list.txt'

engine = create_engine("mysql+pymysql://norberteke:Eepaiz3h@localhost/norberteke")

def process_GH_recent(range_start, range_end):
    conn = engine.connect()

    SQL_query = "SELECT unifiedId, GH_UserId FROM GH_recent_activity"
    data = pd.read_sql_query(SQL_query, conn)
    unifiedID_list = data['unifiedId'].tolist()
    userID_list = data['GH_UserId'].tolist()
    userID_dict = {}
    for idx in range(0, len(unifiedID_list)):
        userID_dict[unifiedID_list[idx]] = int(userID_list[idx])

    for id in unifiedID_list[range_start:range_end]:
        try:
            if id % 200 == 0:
                print("Progress --- ", id, "/", range_end)
            hasCodeReview = False
            hasCommitComment = False

            # ----------------- List of Repo Descriptions, Repo Names, Repo Labels  (Projects)-------------------------------------------------------------
            activity_SQL = "SELECT projects_new.name, description, language, repo_labels_new.name " \
                           "FROM projects_new, repo_labels_new " \
                           "WHERE owner_id = :id AND projects_new.id = repo_labels_new.repo_id AND created_at >= '2016-01-01 00:00:00'"

            param = {"id": userID_dict[id]}
            data = pd.read_sql_query(sql=text(activity_SQL), params=param, con=conn)
            data = data.drop_duplicates(inplace=False)

            repo_names = ""
            repo_desc = ""
            repo_lang = ""
            repo_labels = ""

            if data.empty is False:
                for idx in range(0, data.shape[0]):
                    if data.iloc[:, 0].index.isin([idx]).any():
                        if data.iloc[idx, 0] is not None:
                            if len(data.iloc[idx, 0]) > 5:
                                repo_names = repo_names + " " + process_gh_project_names(data.iloc[idx, 0])
                            else:
                                repo_names = repo_names + " " + data.iloc[idx, 0]
                    if data['description'].index.isin([idx]).any():
                        if data['description'][idx] is not None:
                            repo_desc = repo_desc + " " + data['description'][idx]
                    if data['language'].index.isin([idx]).any():
                        if data['language'][idx] is not None:
                            repo_lang = repo_lang + " " + data['language'][idx]
                    if data.iloc[:, 3].index.isin([idx]).any():
                        if data.iloc[:, 3] is not None:
                            repo_labels = repo_labels + " " + data.iloc[idx, 3]

                repo_names = text_processing.initial_cleaning(repo_names)
                repo_desc = text_processing.initial_cleaning(repo_desc)
                repo_lang = text_processing.initial_cleaning(repo_lang)
                repo_labels = text_processing.initial_cleaning(repo_labels)

                update_st = "UPDATE GH_recent_activity SET repoNames = :text1, repoLabels = :text2, " \
                            "repoDescriptions = :text3, repoLanguages = :text4 WHERE unifiedId = :id"
                param = {"text1": repo_names, "text2": repo_labels, "text3": repo_desc, "text4": repo_lang, "id": int(id)}
                conn.execute(text(update_st), param)

            # ------------------- List of Code review comments (PR_Comm) ---------------------------------------
            activity_SQL = "SELECT body FROM pull_request_comments_new WHERE user_id = :id AND created_at >= '2016-01-01 00:00:00'"

            param = {"id": userID_dict[id]}
            data = pd.read_sql_query(sql=text(activity_SQL), params=param, con=conn)
            data = data.drop_duplicates(inplace=False)

            str = ""
            if data.empty is False:
                for idx in range(0, data.shape[0]):
                    if data['body'].index.isin([idx]).any():
                        if data['body'][idx] is not None:
                            hasCodeReview = True
                            str = str + " " + data['body'][idx]

                cleanedText = text_processing.initial_cleaning(str)
                update_st = "UPDATE GH_recent_activity SET codeReviewComments = :text WHERE unifiedId = :id"
                param = {"text": cleanedText, "id": int(id)}
                conn.execute(text(update_st), param)

            # --------------------- List of Commit comments (Commit Comments) ---------------------------------------
            activity_SQL = "SELECT body FROM commit_comments_new WHERE user_id = :id AND created_at >= '2016-01-01 00:00:00'"

            param = {"id": userID_dict[id]}
            data = pd.read_sql_query(sql=text(activity_SQL), params=param, con=conn)
            data = data.drop_duplicates(inplace=False)

            str = ""
            if data.empty is False:
                for idx in range(0, data.shape[0]):
                    if data['body'].index.isin([idx]).any():
                        if data['body'][idx] is not None:
                            hasCommitComment = True
                            str = str + " " + data['body'][idx]

                cleanedText = text_processing.initial_cleaning(str)
                update_st = "UPDATE GH_recent_activity SET commitCommments = :text WHERE unifiedId = :id"
                param = {"text": cleanedText, "id": int(id)}
                conn.execute(text(update_st), param)

            # --------- get activity status based on whether they have any questions or answers in the past 3 years -------
            active = 0
            if hasCodeReview is True or hasCommitComment is True:
                active = 1
            update_st = "UPDATE GH_recent_activity SET active = :value WHERE unifiedId = :id"
            param = {"value": active, "id": int(id)}
            conn.execute(text(update_st), param)

            # ---- get value of each data field and run the NLP pre-processing script to get the user's full activity -----
            activity_SQL = "SELECT repoNames, repoLabels, repoDescriptions, repoLanguages, codeReviewComments, " \
                           "commitCommments FROM GH_recent_activity WHERE unifiedId = :id"
            param = {"id": int(id)}
            data = pd.read_sql_query(sql=text(activity_SQL), params=param, con=conn)

            str = ""
            if data.shape[0] > 0:
                if data['repoNames'].index.isin([0]).any():
                    if data['repoNames'][0] is not None:
                        str = str + " " + data['repoNames'][0]
                if data['repoDescriptions'].index.isin([0]).any():
                    if data['repoDescriptions'][0] is not None:
                        str = str + " " + data['repoDescriptions'][0]
                if data['repoLanguages'].index.isin([0]).any():
                    if data['repoLanguages'][0] is not None:
                        str = str + " " + data['repoLanguages'][0]
                if data['repoLabels'].index.isin([0]).any():
                    if data['repoLabels'][0] is not None:
                        str = str + " " + data['repoLabels'][0]
                if data['commitCommments'].index.isin([0]).any():
                    if data['commitCommments'][0] is not None:
                        str = str + " " + data['commitCommments'][0]
                if data['codeReviewComments'].index.isin([0]).any():
                    if data['codeReviewComments'][0] is not None:
                        str = str + " " + data['codeReviewComments'][0]

            full_activity = text_processing.NLP_processing(str)
            update_st = "UPDATE GH_recent_activity SET full_activity= :value WHERE unifiedId = :id"
            param = {"value": full_activity, "id": int(id)}
            conn.execute(text(update_st), param)
        except:
            print("Exception has occured at id ", id)
            with open(exceptions_filename_recent, "a") as f:
                f.write("%d" % id)
                f.write("\n")
            continue
    engine.dispose()

def process_GH_past(range_start, range_end):
    conn = engine.connect()

    SQL_query = "SELECT unifiedId, GH_UserId FROM GH_past_activity"
    data = pd.read_sql_query(SQL_query, conn)
    unifiedID_list = data['unifiedId'].tolist()
    userID_list = data['GH_UserId'].tolist()
    userID_dict = {}
    for idx in range(0, len(unifiedID_list)):
        userID_dict[unifiedID_list[idx]] = int(userID_list[idx])

    for id in unifiedID_list[range_start:range_end]:
        try:
            if id % 200 == 0:
                print("Progress --- ", id, "/", range_end)
            hasCodeReview = False
            hasCommitComment = False

            # ----------------- List of Repo Descriptions, Repo Names, Repo Labels  (Projects)-------------------------------------------------------------
            activity_SQL = "SELECT projects_new.name, description, language, repo_labels_new.name " \
                           "FROM projects_new, repo_labels_new " \
                           "WHERE owner_id = :id AND projects_new.id = repo_labels_new.repo_id AND created_at < '2016-01-01 00:00:00'"

            param = {"id": userID_dict[id]}
            data = pd.read_sql_query(sql=text(activity_SQL), params=param, con=conn)
            data = data.drop_duplicates(inplace=False)

            repo_names = ""
            repo_desc = ""
            repo_lang = ""
            repo_labels = ""

            if data.empty is False:
                for idx in range(0, data.shape[0]):
                    if data.iloc[:, 0].index.isin([idx]).any():
                        if data.iloc[idx, 0] is not None:
                            if len(data.iloc[idx, 0]) > 5:
                                repo_names = repo_names + " " + process_gh_project_names(data.iloc[idx, 0])
                            else:
                                repo_names = repo_names + " " + data.iloc[idx, 0]
                    if data['description'].index.isin([idx]).any():
                        if data['description'][idx] is not None:
                            repo_desc = repo_desc + " " + data['description'][idx]
                    if data['language'].index.isin([idx]).any():
                        if data['language'][idx] is not None:
                            repo_lang = repo_lang + " " + data['language'][idx]
                    if data.iloc[:, 3].index.isin([idx]).any():
                        if data.iloc[:, 3] is not None:
                            repo_labels = repo_labels + " " + data.iloc[idx, 3]

                repo_names = text_processing.initial_cleaning(repo_names)
                repo_desc = text_processing.initial_cleaning(repo_desc)
                repo_lang = text_processing.initial_cleaning(repo_lang)
                repo_labels = text_processing.initial_cleaning(repo_labels)

                update_st = "UPDATE GH_past_activity SET repoNames = :text1, repoLabels = :text2, " \
                            "repoDescriptions = :text3, repoLanguages = :text4 WHERE unifiedId = :id"
                param = {"text1": repo_names, "text2": repo_labels, "text3": repo_desc, "text4": repo_lang,
                         "id": int(id)}
                conn.execute(text(update_st), param)

            # ------------------- List of Code review comments (PR_Comm) ---------------------------------------
            activity_SQL = "SELECT body FROM pull_request_comments_new WHERE user_id = :id AND created_at < '2016-01-01 00:00:00'"

            param = {"id": userID_dict[id]}
            data = pd.read_sql_query(sql=text(activity_SQL), params=param, con=conn)
            data = data.drop_duplicates(inplace=False)

            str = ""
            if data.empty is False:
                for idx in range(0, data.shape[0]):
                    if data['body'].index.isin([idx]).any():
                        if data['body'][idx] is not None:
                            hasCodeReview = True
                            str = str + " " + data['body'][idx]

                cleanedText = text_processing.initial_cleaning(str)
                update_st = "UPDATE GH_past_activity SET codeReviewComments = :text WHERE unifiedId = :id"
                param = {"text": cleanedText, "id": int(id)}
                conn.execute(text(update_st), param)

            # --------------------- List of Commit comments (Commit Comments) ---------------------------------------
            activity_SQL = "SELECT body FROM commit_comments_new WHERE user_id = :id AND created_at < '2016-01-01 00:00:00'"

            param = {"id": userID_dict[id]}
            data = pd.read_sql_query(sql=text(activity_SQL), params=param, con=conn)
            data = data.drop_duplicates(inplace=False)

            str = ""
            if data.empty is False:
                for idx in range(0, data.shape[0]):
                    if data['body'].index.isin([idx]).any():
                        if data['body'][idx] is not None:
                            hasCommitComment = True
                            str = str + " " + data['body'][idx]

                cleanedText = text_processing.initial_cleaning(str)
                update_st = "UPDATE GH_past_activity SET commitCommments = :text WHERE unifiedId = :id"
                param = {"text": cleanedText, "id": int(id)}
                conn.execute(text(update_st), param)

            # --------- get activity status based on whether they have any questions or answers in the past 3 years -------
            active = 0
            if hasCodeReview is True or hasCommitComment is True:
                active = 1
            update_st = "UPDATE GH_past_activity SET active = :value WHERE unifiedId = :id"
            param = {"value": active, "id": int(id)}
            conn.execute(text(update_st), param)

            # ---- get value of each data field and run the NLP pre-processing script to get the user's full activity -----
            activity_SQL = "SELECT repoNames, repoLabels, repoDescriptions, repoLanguages, codeReviewComments, " \
                           "commitCommments FROM GH_past_activity WHERE unifiedId = :id"
            param = {"id": int(id)}
            data = pd.read_sql_query(sql=text(activity_SQL), params=param, con=conn)

            str = ""
            if data.shape[0] > 0:
                if data['repoNames'].index.isin([0]).any():
                    if data['repoNames'][0] is not None:
                        str = str + " " + data['repoNames'][0]
                if data['repoDescriptions'].index.isin([0]).any():
                    if data['repoDescriptions'][0] is not None:
                        str = str + " " + data['repoDescriptions'][0]
                if data['repoLanguages'].index.isin([0]).any():
                    if data['repoLanguages'][0] is not None:
                        str = str + " " + data['repoLanguages'][0]
                if data['repoLabels'].index.isin([0]).any():
                    if data['repoLabels'][0] is not None:
                        str = str + " " + data['repoLabels'][0]
                if data['commitCommments'].index.isin([0]).any():
                    if data['commitCommments'][0] is not None:
                        str = str + " " + data['commitCommments'][0]
                if data['codeReviewComments'].index.isin([0]).any():
                    if data['codeReviewComments'][0] is not None:
                        str = str + " " + data['codeReviewComments'][0]

            full_activity = text_processing.NLP_processing(str)
            update_st = "UPDATE GH_past_activity SET full_activity= :value WHERE unifiedId = :id"
            param = {"value": full_activity, "id": int(id)}
            conn.execute(text(update_st), param)
        except:
            print("Exception has occured at id ", id)
            with open(exceptions_filename_past, "a") as f:
                f.write("%d" % id)
                f.write("\n")
            continue
    engine.dispose()

def process_gh_project_names(text):
    if '-' in text:
        return ' '.join(text.split('-'))
    elif text[0].isupper():
        return ''.join(map(lambda x: x if x.islower() else " " + x, text[0].lower() + text[1:]))
    else:
        return ''.join(map(lambda x: x if x.islower() else " " + x, text))