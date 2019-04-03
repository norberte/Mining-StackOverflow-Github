-- filter commits table --> keep only commits related to the project id that are in the projects_linked table
CREATE TABLE commits_linked AS
SELECT * FROM commits
WHERE project_id IN ( SELECT DISTINCT GH_project_id FROM projects_linked);


ALTER TABLE commits_linked ADD CONSTRAINT `commits_linked_pk` PRIMARY KEY (id);
ALTER TABLE commits_linked ADD CONSTRAINT `commits_linked_fk1` FOREIGN KEY (author_id) REFERENCES GH_users (id);
ALTER TABLE commits_linked ADD CONSTRAINT `commits_linked_fk2` FOREIGN KEY (committer_id) REFERENCES GH_users (id);
ALTER TABLE commits_linked ADD CONSTRAINT `commits_linked_fk3` FOREIGN KEY (project_id) REFERENCES projects_linked (GH_project_id);
DROP TABLE commits;


-- filter project_members table --> keep only project_members with repo_id that are in the projects_linked table
CREATE TABLE project_members_linked AS
SELECT * FROM project_members
WHERE repo_id IN (SELECT DISTINCT GH_project_id FROM projects_linked);

ALTER TABLE project_members_linked ADD CONSTRAINT `project_members_linked_ppk` PRIMARY KEY (repo_id, user_id);
ALTER TABLE project_members_linked ADD CONSTRAINT `project_members_linked_fk1` FOREIGN KEY (repo_id) REFERENCES projects_linked (GH_project_id);
ALTER TABLE project_members_linked ADD CONSTRAINT `project_members_linked_fk2` FOREIGN KEY (user_id) REFERENCES GH_users (id);
DROP TABLE project_members;


-- filter repo_labels table --> keep only repo_labels with repo_id that are in the projects_linked table
CREATE TABLE repo_labels_linked AS
SELECT * FROM repo_labels
WHERE repo_id IN (SELECT DISTINCT GH_project_id FROM projects_linked);

ALTER TABLE repo_labels_linked ADD CONSTRAINT `repo_labels_linked_pk` PRIMARY KEY (id);
ALTER TABLE repo_labels_linked ADD CONSTRAINT `repo_labels_linked_fk` FOREIGN KEY (repo_id) REFERENCES projects_linked (GH_project_id);
DROP TABLE repo_labels;


-- filter watchers table --> keep only watchers with repo_id that are in the projects_linked table
CREATE TABLE watchers_linked AS
SELECT * FROM watchers
WHERE repo_id IN (SELECT DISTINCT GH_project_id FROM projects_linked);

ALTER TABLE watchers_linked ADD CONSTRAINT `watchers_linked_ppk` PRIMARY KEY (repo_id, user_id);  
ALTER TABLE watchers_linked ADD CONSTRAINT `watchers_linked_fk1` FOREIGN KEY (repo_id) REFERENCES projects_linked (GH_project_id);
ALTER TABLE watchers_linked ADD CONSTRAINT `watchers_linked_fk2` FOREIGN KEY (user_id) REFERENCES GH_users (id);
DROP TABLE watchers;


-- filter project_languages table --> keep only project_languages with project_id that are in the projects_linked table
CREATE TABLE project_languages_linked AS
SELECT * FROM project_languages
WHERE project_id IN (SELECT DISTINCT GH_project_id FROM projects_linked);

ALTER TABLE project_languages_linked ADD CONSTRAINT `project_languages_linked_fk` FOREIGN KEY (project_id) REFERENCES projects_linked (GH_project_id);
DROP TABLE project_languages;


-- filter project_topics table --> keep only project_topics with project_id that are in the projects_linked table
CREATE TABLE project_topics_linked AS
SELECT * FROM project_topics
WHERE project_id IN (SELECT DISTINCT GH_project_id FROM projects_linked);

ALTER TABLE project_topics_linked ADD CONSTRAINT `project_topics_linked_ppk` PRIMARY KEY (project_id, topic_name);
ALTER TABLE project_topics_linked ADD CONSTRAINT `project_topics_linked_fk` FOREIGN KEY (project_id) REFERENCES projects_linked (GH_project_id);
DROP TABLE project_topics;

-- filter commit_comments table --> keep only commit_comments with commit_id that are in the commit_linked table
CREATE TABLE commit_comments_linked AS
SELECT * FROM commit_comments
WHERE commit_id IN (SELECT id FROM commits_linked);


ALTER TABLE commit_comments_linked ADD CONSTRAINT `commit_comments_linked_pk` PRIMARY KEY (id);
ALTER TABLE commit_comments_linked ADD CONSTRAINT `commit_comments_linked_fk1` FOREIGN KEY (commit_id) REFERENCES commits_linked (id);
ALTER TABLE commit_comments_linked ADD CONSTRAINT `commit_comments_linked_fk2` FOREIGN KEY (user_id) REFERENCES GH_users (id);
DROP TABLE commit_comments;


-- filter commit_parents table --> keep only commit_parents with commit_id that are in the commit_linked table
CREATE INDEX `commits_id_linked` ON commits_linked (id);
CREATE TABLE commit_parents_linked AS
SELECT * FROM commit_parents
WHERE commit_id IN (SELECT id FROM commits_linked) AND parent_id IN (SELECT id FROM commits_linked);

DELETE FROM commit_parents WHERE commit_id NOT IN (SELECT id FROM commits_linked) AND parent_id NOT IN (SELECT id FROM commits_linked); -- did not finish running


ALTER TABLE commit_parents_linked ADD CONSTRAINT `commit_parents_linked_fk1` FOREIGN KEY (commit_id) REFERENCES commits_linked (id);  
ALTER TABLE commit_parents_linked ADD CONSTRAINT `commit_parents_linked_fk2` FOREIGN KEY (parent_id) REFERENCES commits_linked (id);
DROP TABLE commit_parents;


-- filter pull_requests table --> keep only commit_id and project_id that are in the commits_linked and project_linked tables
CREATE TABLE pull_requests_linked AS
SELECT * FROM pull_requests
WHERE head_commit_id IN (SELECT id FROM commits_linked) and base_commit_id IN (SELECT id FROM commits_linked) 
and head_repo_id IN (SELECT DISTINCT GH_project_id FROM projects_linked) and base_repo_id IN (SELECT DISTINCT GH_project_id FROM projects_linked);


ALTER TABLE pull_requests_linked ADD CONSTRAINT `pull_requests_linked_pk` PRIMARY KEY (`id`);
ALTER TABLE pull_requests_linked ADD CONSTRAINT `pull_requests_linked_fk1` FOREIGN KEY (`head_repo_id`) REFERENCES projects_linked (GH_project_id);
ALTER TABLE pull_requests_linked ADD CONSTRAINT `pull_requests_linked_fk2` FOREIGN KEY (`base_repo_id`) REFERENCES projects_linked (GH_project_id);
ALTER TABLE pull_requests_linked ADD CONSTRAINT `pull_requests_linked_fk3` FOREIGN KEY (`head_commit_id`) REFERENCES commits_linked (id);
ALTER TABLE pull_requests_linked ADD CONSTRAINT `pull_requests_linked_fk4` FOREIGN KEY (`base_commit_id`) REFERENCES commits_linked (id);
DROP TABLE pull_requests;


-- filter project_commits table --> keep only commit_id and project_id that are in the commits_linked and project_linked tables
CREATE TABLE project_commits_linked AS SELECT project_id, id FROM commits_linked; 
ALTER TABLE project_commits_linked ADD CONSTRAINT `project_commits_linked_fk1` FOREIGN KEY (project_id) REFERENCES projects_linked (GH_project_id);
ALTER TABLE project_commits_linked ADD CONSTRAINT `project_commits_linked_fk2` FOREIGN KEY (id) REFERENCES commits_linked (id); -- running now



-- filter pull_request_comments table --> keep only commit_id and pull_request_id that are in the commits_linked and pull_requests_linked tables
CREATE TABLE pull_request_comments_linked AS
SELECT * FROM pull_request_comments
WHERE pull_request_id IN (SELECT id FROM pull_requests_linked) and commit_id IN (SELECT id FROM commits_linked);


 
ALTER TABLE pull_request_comments_linked ADD CONSTRAINT `pull_request_comments_linked_fk1` FOREIGN KEY (pull_request_id) REFERENCES pull_requests_linked(id);
ALTER TABLE pull_request_comments_linked ADD CONSTRAINT `pull_request_comments_linked_fk2` FOREIGN KEY (user_id) REFERENCES GH_users (id); 
ALTER TABLE pull_request_comments_linked ADD CONSTRAINT `pull_request_comments_linked_fk3` FOREIGN KEY (commit_id) REFERENCES commits_linked (id);
DROP TABLE pull_request_comments;	
	
	
	
-- filter pull_request_commits table --> keep only commit_id and pull_request_id that are in the commits_linked and pull_requests_linkes tables
CREATE TABLE pull_request_commits_linked AS
SELECT * FROM pull_request_commits
WHERE pull_request_id IN (SELECT id FROM pull_requests_linked) and commit_id IN (SELECT id FROM commits_linked);


ALTER TABLE pull_request_commits_linked ADD CONSTRAINT `pull_request_commits_linked_pk` PRIMARY KEY (pull_request_id, commit_id);
ALTER TABLE pull_request_commits_linked ADD CONSTRAINT `pull_request_commits_linked_fk1` FOREIGN KEY (pull_request_id) REFERENCES pull_requests_linked(id);
ALTER TABLE pull_request_commits_linked ADD CONSTRAINT `pull_request_commits_linked_fk2` FOREIGN KEY (commit_id) REFERENCES commits_linked(id); -- does not run
DROP TABLE pull_request_commits;

	
	
-- filter pull_request_history table --> keep only pull_request_id that are in the pull_requests_linkes table	
CREATE TABLE pull_request_history_linked AS
SELECT * FROM pull_request_history
WHERE pull_request_id IN (SELECT id FROM pull_requests_linked);


ALTER TABLE pull_request_history_linked ADD CONSTRAINT `pull_request_history_linked_pk` PRIMARY KEY (id);
ALTER TABLE pull_request_history_linked ADD CONSTRAINT `pull_request_history_linked_fk1` FOREIGN KEY (pull_request_id) REFERENCES pull_requests_linked(id);
ALTER TABLE pull_request_history_linked ADD CONSTRAINT `pull_request_history_linked_fk2` FOREIGN KEY (actor_id) REFERENCES GH_users(id);  -- does not run
DROP TABLE pull_request_history;


-- filter issues table --> keep only pull_request_id and repo_id that are in the pull_requests_linkes and projects_linked tables
CREATE TABLE issues_linked AS
SELECT * FROM issues
WHERE repo_id IN (SELECT id FROM projects_linked) AND pull_request_id IN (SELECT id FROM pull_requests_linked);


ALTER TABLE issues_linked ADD CONSTRAINT `issues_linked_pk` PRIMARY KEY (id);
ALTER TABLE issues_linked ADD CONSTRAINT `issues_linked_fk1` FOREIGN KEY (repo_id) REFERENCES projects_linked(id); -- does not run
ALTER TABLE issues_linked ADD CONSTRAINT `issues_linked_fk2` FOREIGN KEY (reporter_id) REFERENCES GH_users(id); -- does not run
ALTER TABLE issues_linked ADD CONSTRAINT `issues_linked_fk3` FOREIGN KEY (assignee_id) REFERENCES GH_users(id);
ALTER TABLE issues_linked ADD CONSTRAINT `issues_linked_fk4` FOREIGN KEY (pull_request_id) REFERENCES pull_requests_linked(id);
DROP TABLE issues;



-- filter issue_comments table --> keep only issue_id that are in the issues_linked table
CREATE TABLE issue_comments_linked AS
SELECT * FROM issue_comments
WHERE issue_id IN (SELECT id FROM issues_linked);


ALTER TABLE issue_comments_linked ADD CONSTRAINT `issue_comments_linked_fk1` FOREIGN KEY (issue_id) REFERENCES issues_linked(id); -- does not run
ALTER TABLE issue_comments_linked ADD CONSTRAINT `issue_comments_linked_fk2` FOREIGN KEY (user_id) REFERENCES GH_users(id);
DROP TABLE issue_comments;



-- filter issue_events table --> keep only issue_id that are in the issues_linked table
CREATE TABLE issue_events_linked AS
SELECT * FROM issue_events
WHERE issue_id IN (SELECT id FROM issues_linked);


ALTER TABLE issue_events_linked ADD CONSTRAINT `issue_events_linked_fk1` FOREIGN KEY (issue_id) REFERENCES issues_linked(id);
ALTER TABLE issue_events_linked ADD CONSTRAINT `issue_events_linked_fk2` FOREIGN KEY (actor_id) REFERENCES GH_users(id);
DROP TABLE issue_events;



-- filter issue_labels table --> keep only issue_id and label_id that are in the issues_linked and repo_labels_linked tables
CREATE TABLE issue_labels_linked AS
SELECT * FROM issue_labels
WHERE issue_id IN (SELECT id FROM issues_linked);

ALTER TABLE issue_labels_linked ADD CONSTRAINT `issue_labels_linked_pk` PRIMARY KEY (issue_id, label_id);
ALTER TABLE issue_labels_linked ADD CONSTRAINT `issue_labels_linked_fk1` FOREIGN KEY (label_id) REFERENCES repo_labels_linked(id);
ALTER TABLE issue_labels_linked ADD CONSTRAINT `issue_labels_linked_fk2` FOREIGN KEY (issue_id) REFERENCES issues_linked(id);
DROP TABLE issue_labels;