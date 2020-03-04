from sqlalchemy import create_engine
from sqlalchemy.sql import text
import text_processing
import pandas as pd
import logging
import math
logging.basicConfig(filename='/home/norberteke/PycharmProjects/Thesis/logs/clean_aggregate_data_for_LDA.log', format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

exceptions_filename = '/home/norberteke/PycharmProjects/Thesis/data_cleaning/SO_past_exceptions_id_list.txt'
exceptions_filename_recent = '/home/norberteke/PycharmProjects/Thesis/data_cleaning/SO_recent_exceptions_id_list.txt'

engine = create_engine("mysql+pymysql://norberteke:Eepaiz3h@localhost/norberteke")

def process_SO_recent(range_start, range_end):
    conn = engine.connect()

    SQL_query = "SELECT unifiedId, SO_UserId FROM SO_recent_activity"
    data = pd.read_sql_query(SQL_query, conn)
    unifiedID_list = data['unifiedId'].tolist()
    userID_list = data['SO_UserId'].tolist()
    userID_dict = {}
    for idx in range(0, len(unifiedID_list)):
        userID_dict[unifiedID_list[idx]] = int(userID_list[idx])

    for id in unifiedID_list[range_start:range_end]:
        try:
            if id % 200 == 0:
                print("Progress --- ", id, "/", range_end)
            hasQuestions = False
            hasAnswers = False
            # ----------------- get about me from Users table -------------------------------------------------------------
            aboutMe_SQL = "SELECT AboutMe FROM SO_Users WHERE Id = :id"
            param = {"id": userID_dict[id]}
            data = pd.read_sql_query(sql=text(aboutMe_SQL), params=param, con=conn)

            if data['AboutMe'].empty is False:
                if data['AboutMe'].index.isin([(0,)]).any():
                    if data['AboutMe'][0] is not None:
                        cleanedText = text_processing.initial_cleaning(data['AboutMe'][0])
                        update_st = "UPDATE SO_recent_activity SET aboutMe = :text WHERE unifiedId = :id"
                        param = {"text": cleanedText, "id": int(id)}
                        conn.execute(text(update_st), param)

            # ------------------- get badges from Badges table -----------------------------------------------------------
            badges_SQL = "SELECT Name FROM badges_new WHERE UserId = :id AND Date >= '2016-01-01 00:00:00'"
            param = {"id": userID_dict[id]}
            data = pd.read_sql_query(sql=text(badges_SQL), params=param, con=conn)

            if data['Name'].empty is False:
                if data['Name'][0] is not None:
                    cleanedText = ' '.join(data['Name'].to_list())
                    update_st = "UPDATE SO_recent_activity SET badges = :text WHERE unifiedId = :id"
                    param = {"text": cleanedText, "id": int(id)}
                    conn.execute(text(update_st), param)

            # --------------------------- get list of comment bodies, and the posts that they belong to -------------------
            comments_SQL = "SELECT comments_new.Text, Posts.Body, Posts.Tags, Posts.Title " \
                           "FROM comments_new, Posts " \
                           "WHERE comments_new.PostId = Posts.Id AND comments_new.UserId = :id AND " \
                           "comments_new.CreationDate >= '2016-01-01 00:00:00' ORDER BY comments_new.UserId"

            param = {"id": userID_dict[id]}
            data = pd.read_sql_query(sql=text(comments_SQL), params=param, con=conn)
            str = ""
            if data.empty is False:
                for idx in range(0, data.shape[0]):
                    if data['Title'].index.isin([idx]).any():
                        if data['Title'][idx] is not None:
                            str = str + " " + data['Title'][idx]
                    if data['Tags'].index.isin([idx]).any():
                        if data['Tags'][idx] is not None:
                            str = str + " " + text_processing.tags_cleaning(data['Tags'][idx])
                    if data['Body'].index.isin([idx]).any():
                        if data['Body'][idx] is not None:
                            str = str + " " + data['Body'][idx]
                    if data['Text'].index.isin([idx]).any():
                        if data['Text'][idx] is not None:
                            str = str + " " + data['Text'][idx]

                cleanedText = text_processing.initial_cleaning(str)
                update_st = "UPDATE SO_recent_activity SET commentData = :text WHERE unifiedId = :id"
                param = {"text": cleanedText, "id": int(id)}
                conn.execute(text(update_st), param)

            # -------------get Post tags, titles, body for Questions, and get accepted answer, if exists------------------
            question_SQL = "SELECT AcceptedAnswerId, Body, Title, Tags FROM posts_new " \
                           "WHERE PostTypeId = 1 AND OwnerUserId = :id AND CreationDate >= '2016-01-01 00:00:00'"

            param = {"id": userID_dict[id]}
            data = pd.read_sql_query(sql=text(question_SQL), params=param, con=conn)
            data = data.drop_duplicates(inplace=False)

            if data.empty is False:  # check if user asked questions
                str = ""
                hasQuestions = True
                for idx in range(0, data.shape[0]):
                    if data['Title'].index.isin([idx]).any():
                        if data['Title'][idx] is not None:
                            str = str + " " + data['Title'][idx]
                    if data['Tags'].index.isin([idx]).any():
                        if data['Tags'][idx] is not None:
                            str = str + " " + text_processing.tags_cleaning(data['Tags'][idx])
                    if data['Body'].index.isin([idx]).any():
                        if data['Body'][idx] is not None:
                            str = str + " " + data['Body'][idx]
                    if data['AcceptedAnswerId'].index.isin([idx]).any():
                        if data['AcceptedAnswerId'][idx] is not None:
                            if math.isnan(data['AcceptedAnswerId'][idx]) is False:
                                accepted_answer_SQL = "SELECT Body FROM Posts WHERE Id = :id"
                                param = {"id": int(data['AcceptedAnswerId'][idx])}
                                accepted_answer = pd.read_sql_query(sql=text(accepted_answer_SQL), params=param,
                                                                    con=conn)
                                if accepted_answer['Body'].index.isin([(0,)]).any():
                                    str = str + " " + accepted_answer['Body'][0]

                cleanedText = text_processing.initial_cleaning(str)
                update_st = "UPDATE SO_recent_activity SET postQuestions = :text WHERE unifiedId = :id"
                param = {"text": cleanedText, "id": int(id)}
                conn.execute(text(update_st), param)

            # -------------get Post tags, titles, body for Answers, and the original question that was asked --------------
            answer_SQL = "SELECT posts_new.Body, Posts.Body, Posts.Tags, Posts.Title FROM posts_new, Posts " \
                         "WHERE posts_new.PostTypeId = 2 AND posts_new.ParentId = Posts.Id " \
                         "AND posts_new.OwnerUserId = :id AND posts_new.CreationDate >= '2016-01-01 00:00:00'"

            param = {"id": userID_dict[id]}
            data = pd.read_sql_query(sql=text(answer_SQL), params=param, con=conn)
            data = data.drop_duplicates(inplace=False)

            if data.empty is False:  # check if user has answered any questions
                str = ""
                hasAnswers = True
                for idx in range(0, data.shape[0]):
                    if data['Title'].index.isin([idx]).any():
                        if data['Title'][idx] is not None:
                            str = str + " " + data['Title'][idx]
                    if data['Tags'].index.isin([idx]).any():
                        if data['Tags'][idx] is not None:
                            str = str + " " + text_processing.tags_cleaning(data['Tags'][idx])
                    if data.iloc[:, 1].index.isin(
                            [idx]).any():  # 2 columns are named Body, so need to access numerically
                        if data.iloc[idx, 1] is not None:
                            str = str + " " + data.iloc[idx, 1]
                    if data.iloc[:, 0].index.isin([idx]).any():
                        if data.iloc[idx, 0] is not None:
                            str = str + " " + data.iloc[idx, 0]

                cleanedText = text_processing.initial_cleaning(str)
                update_st = "UPDATE SO_recent_activity SET postAnswers = :text WHERE unifiedId = :id"
                param = {"text": cleanedText, "id": int(id)}
                conn.execute(text(update_st), param)

            # --------- get activity status based on whether they have any questions or answers in the past 3 years -------
            active = 0
            if hasQuestions is True or hasAnswers is True:
                active = 1
            update_st = "UPDATE SO_recent_activity SET active = :value WHERE unifiedId = :id"
            param = {"value": active, "id": int(id)}
            conn.execute(text(update_st), param)

            # ---- get value of each data field and run the NLP pre-processing script to get the user's full activity -----
            activity_SQL = "SELECT badges, aboutMe, postAnswers, postQuestions, commentData FROM SO_recent_activity " \
                           "WHERE unifiedId = :id"
            param = {"id": int(id)}
            data = pd.read_sql_query(sql=text(activity_SQL), params=param, con=conn)
            str = ""
            if data.shape[0] > 0:
                if data['badges'].index.isin([(0,)]).any():
                    if data['badges'][0] is not None:
                        str = str + " " + data['badges'][0]
                if data['aboutMe'].index.isin([(0,)]).any():
                    if data['aboutMe'][0] is not None:
                        str = str + " " + data['aboutMe'][0]
                if data['postAnswers'].index.isin([(0,)]).any():
                    if data['postAnswers'][0] is not None:
                        str = str + " " + data['postAnswers'][0]
                if data['postQuestions'].index.isin([(0,)]).any():
                    if data['postQuestions'][0] is not None:
                        str = str + " " + data['postQuestions'][0]
                if data['commentData'].index.isin([(0,)]).any():
                    if data['commentData'][0] is not None:
                        str = str + " " + data['commentData'][0]

            full_activity = text_processing.NLP_processing(str)

            update_st = "UPDATE SO_recent_activity SET full_activity= :value WHERE unifiedId = :id"
            param = {"value": full_activity, "id": int(id)}
            conn.execute(text(update_st), param)
        except:
            print("Exception has occured at id ", id)
            with open(exceptions_filename_recent, "a") as f:
                f.write("%d" % id)
                f.write("\n")
            continue
    engine.dispose()

def process_SO_past(range_start, range_end):
    conn = engine.connect()

    SQL_query = "SELECT unifiedId, SO_UserId FROM SO_past_activity"
    data = pd.read_sql_query(SQL_query, conn)
    unifiedID_list = data['unifiedId'].tolist()
    userID_list = data['SO_UserId'].tolist()
    userID_dict = {}
    for idx in range(0, len(unifiedID_list)):
        userID_dict[unifiedID_list[idx]] = int(userID_list[idx])

    for id in unifiedID_list[range_start:range_end]:
        try:
            if id % 200 == 0:
                print("Progress --- ", id, "/", range_end)
            hasQuestions = False
            hasAnswers = False
            # ----------------- get about me from Users table -------------------------------------------------------------
            aboutMe_SQL = "SELECT AboutMe FROM SO_Users WHERE Id = :id"
            param = {"id": userID_dict[id]}
            data = pd.read_sql_query(sql=text(aboutMe_SQL), params=param, con=conn)

            if data['AboutMe'].empty is False:
                if data['AboutMe'].index.isin([(0,)]).any():
                    if data['AboutMe'][0] is not None:
                        cleanedText = text_processing.initial_cleaning(data['AboutMe'][0])
                        update_st = "UPDATE SO_past_activity SET aboutMe = :text WHERE unifiedId = :id"
                        param = {"text": cleanedText, "id": int(id)}
                        conn.execute(text(update_st), param)

            # ------------------- get badges from Badges table -----------------------------------------------------------
            badges_SQL = "SELECT Name FROM badges_new WHERE UserId = :id AND Date < '2016-01-01 00:00:00'"
            param = {"id": userID_dict[id]}
            data = pd.read_sql_query(sql=text(badges_SQL), params=param, con=conn)

            if data['Name'].empty is False:
                if data['Name'][0] is not None:
                    cleanedText = ' '.join(data['Name'].to_list())
                    update_st = "UPDATE SO_past_activity SET badges = :text WHERE unifiedId = :id"
                    param = {"text": cleanedText, "id": int(id)}
                    conn.execute(text(update_st), param)

            # --------------------------- get list of comment bodies, and the posts that they belong to -------------------
            comments_SQL = "SELECT comments_new.Text, Posts.Body, Posts.Tags, Posts.Title " \
                           "FROM comments_new, Posts " \
                           "WHERE comments_new.PostId = Posts.Id AND comments_new.UserId = :id AND " \
                           "comments_new.CreationDate < '2016-01-01 00:00:00' ORDER BY comments_new.UserId"

            param = {"id": userID_dict[id]}
            data = pd.read_sql_query(sql=text(comments_SQL), params=param, con=conn)
            str = ""
            if data.empty is False:
                for idx in range(0, data.shape[0]):
                    if data['Title'].index.isin([idx]).any():
                        if data['Title'][idx] is not None:
                            str = str + " " + data['Title'][idx]
                    if data['Tags'].index.isin([idx]).any():
                        if data['Tags'][idx] is not None:
                            str = str + " " + text_processing.tags_cleaning(data['Tags'][idx])
                    if data['Body'].index.isin([idx]).any():
                        if data['Body'][idx] is not None:
                            str = str + " " + data['Body'][idx]
                    if data['Text'].index.isin([idx]).any():
                        if data['Text'][idx] is not None:
                            str = str + " " + data['Text'][idx]

                cleanedText = text_processing.initial_cleaning(str)
                update_st = "UPDATE SO_past_activity SET commentData = :text WHERE unifiedId = :id"
                param = {"text": cleanedText, "id": int(id)}
                conn.execute(text(update_st), param)

            # -------------get Post tags, titles, body for Questions, and get accepted answer, if exists------------------
            question_SQL = "SELECT AcceptedAnswerId, Body, Title, Tags FROM posts_new " \
                           "WHERE PostTypeId = 1 AND OwnerUserId = :id AND CreationDate < '2016-01-01 00:00:00'"

            param = {"id": userID_dict[id]}
            data = pd.read_sql_query(sql=text(question_SQL), params=param, con=conn)
            data = data.drop_duplicates(inplace=False)

            if data.empty is False:  # check if user asked questions
                str = ""
                hasQuestions = True
                for idx in range(0, data.shape[0]):
                    if data['Title'].index.isin([idx]).any():
                        if data['Title'][idx] is not None:
                            str = str + " " + data['Title'][idx]
                    if data['Tags'].index.isin([idx]).any():
                        if data['Tags'][idx] is not None:
                            str = str + " " + text_processing.tags_cleaning(data['Tags'][idx])
                    if data['Body'].index.isin([idx]).any():
                        if data['Body'][idx] is not None:
                            str = str + " " + data['Body'][idx]
                    if data['AcceptedAnswerId'].index.isin([idx]).any():
                        if data['AcceptedAnswerId'][idx] is not None:
                            if math.isnan(data['AcceptedAnswerId'][idx]) is False:
                                accepted_answer_SQL = "SELECT Body FROM Posts WHERE Id = :id"
                                param = {"id": int(data['AcceptedAnswerId'][idx])}
                                accepted_answer = pd.read_sql_query(sql=text(accepted_answer_SQL), params=param, con=conn)
                                if accepted_answer['Body'].index.isin([(0,)]).any():
                                    str = str + " " + accepted_answer['Body'][0]

                cleanedText = text_processing.initial_cleaning(str)
                update_st = "UPDATE SO_past_activity SET postQuestions = :text WHERE unifiedId = :id"
                param = {"text": cleanedText, "id": int(id)}
                conn.execute(text(update_st), param)

            # -------------get Post tags, titles, body for Answers, and the original question that was asked --------------
            answer_SQL = "SELECT posts_new.Body, Posts.Body, Posts.Tags, Posts.Title FROM posts_new, Posts " \
                         "WHERE posts_new.PostTypeId = 2 AND posts_new.ParentId = Posts.Id " \
                         "AND posts_new.OwnerUserId = :id AND posts_new.CreationDate < '2016-01-01 00:00:00'"

            param = {"id": userID_dict[id]}
            data = pd.read_sql_query(sql=text(answer_SQL), params=param, con=conn)
            data = data.drop_duplicates(inplace=False)

            if data.empty is False:  # check if user has answered any questions
                str = ""
                hasAnswers = True
                for idx in range(0, data.shape[0]):
                    if data['Title'].index.isin([idx]).any():
                        if data['Title'][idx] is not None:
                            str = str + " " + data['Title'][idx]
                    if data['Tags'].index.isin([idx]).any():
                        if data['Tags'][idx] is not None:
                            str = str + " " + text_processing.tags_cleaning(data['Tags'][idx])
                    if data.iloc[:,1].index.isin([idx]).any():  # 2 columns are named Body, so need to access numerically
                        if data.iloc[idx,1] is not None:
                            str = str + " " + data.iloc[idx,1]
                    if data.iloc[:,0].index.isin([idx]).any():
                        if data.iloc[idx,0] is not None:
                            str = str + " " + data.iloc[idx,0]

                cleanedText = text_processing.initial_cleaning(str)
                update_st = "UPDATE SO_past_activity SET postAnswers = :text WHERE unifiedId = :id"
                param = {"text": cleanedText, "id": int(id)}
                conn.execute(text(update_st), param)

            # --------- get activity status based on whether they have any questions or answers in the past 3 years -------
            active = 0
            if hasQuestions is True or hasAnswers is True:
                active = 1
            update_st = "UPDATE SO_past_activity SET active = :value WHERE unifiedId = :id"
            param = {"value": active, "id": int(id)}
            conn.execute(text(update_st), param)

            # ---- get value of each data field and run the NLP pre-processing script to get the user's full activity -----
            activity_SQL = "SELECT badges, aboutMe, postAnswers, postQuestions, commentData FROM SO_past_activity " \
                           "WHERE unifiedId = :id"
            param = {"id": int(id)}
            data = pd.read_sql_query(sql=text(activity_SQL), params=param, con=conn)
            str = ""
            if data.shape[0] > 0:
                if data['badges'].index.isin([(0,)]).any():
                    if data['badges'][0] is not None:
                        str = str + " " + data['badges'][0]
                if data['aboutMe'].index.isin([(0,)]).any():
                    if data['aboutMe'][0] is not None:
                        str = str + " " + data['aboutMe'][0]
                if data['postAnswers'].index.isin([(0,)]).any():
                    if data['postAnswers'][0] is not None:
                        str = str + " " + data['postAnswers'][0]
                if data['postQuestions'].index.isin([(0,)]).any():
                    if data['postQuestions'][0] is not None:
                        str = str + " " + data['postQuestions'][0]
                if data['commentData'].index.isin([(0,)]).any():
                    if data['commentData'][0] is not None:
                        str = str + " " + data['commentData'][0]


            full_activity = text_processing.NLP_processing(str)

            update_st = "UPDATE SO_past_activity SET full_activity= :value WHERE unifiedId = :id"
            param = {"value": full_activity, "id": int(id)}
            conn.execute(text(update_st), param)
        except:
            print("Exception has occured at id ", id)
            with open(exceptions_filename, "a") as f:
                f.write("%d" % id)
                f.write("\n")
            continue
    engine.dispose()

if __name__ == '__main__':
    engine = create_engine("mysql+pymysql://norberteke:Eepaiz3h@localhost/norberteke")
    conn = engine.connect()

    activity_SQL = "SELECT badges, aboutMe, postAnswers, postQuestions, commentData FROM SO_past_activity"

    data = pd.read_sql_query(sql=text(activity_SQL), con=conn)

    for idx in range (3000, data.shape[0]):
        if idx % 10000 == 0:
            print(idx)
        str = ""
        if data['badges'].index.isin([idx]).any():
            if data['badges'][idx] is not None:
                str = str + " " + data['badges'][idx]
        if data['aboutMe'].index.isin([idx]).any():
            if data['aboutMe'][idx] is not None:
                str = str + " " + data['aboutMe'][idx]
        if data['postAnswers'].index.isin([idx]).any():
            if data['postAnswers'][idx] is not None:
                str = str + " " + data['postAnswers'][idx]
        if data['postQuestions'].index.isin([idx]).any():
            if data['postQuestions'][idx] is not None:
                str = str + " " + data['postQuestions'][idx]
        if data['commentData'].index.isin([idx]).any():
            if data['commentData'][idx] is not None:
                str = str + " " + data['commentData'][idx]

        full_activity = text_processing.NLP_processing(str)

        update_st = "UPDATE SO_past_activity SET full_activity= :value WHERE unifiedId = :id"
        param = {"value": full_activity, "id": int(idx) + 1}
        conn.execute(text(update_st), param)
    engine.dispose()