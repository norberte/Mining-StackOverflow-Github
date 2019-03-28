-- filter commits table --> keep only commits related to the project id that are in the projects_linked table
CREATE TABLE commits_linked AS
SELECT * FROM commits
WHERE project_id IN ( SELECT DISTINCT GH_project_id FROM projects_linked);


ALTER TABLE commits_linked ADD CONSTRAINT `commits_linked_pk` PRIMARY KEY (id);
ALTER TABLE commits_linked ADD CONSTRAINT `commits_linked_fk1` FOREIGN KEY (author_id) REFERENCES GH_users (id);
ALTER TABLE commits_linked ADD CONSTRAINT `commits_linked_fk2` FOREIGN KEY (committer_id) REFERENCES GH_users (id);
ALTER TABLE commits_linked ADD CONSTRAINT `commits_linked_fk3` FOREIGN KEY (project_id) REFERENCES projects_linked (GH_project_id);
DROP TABLE commits;
-- until here

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



-- to be run:
CREATE TABLE commit_comments_linked AS
SELECT * FROM commit_comments
WHERE commit_id IN (SELECT id FROM commits_linked);

ALTER TABLE commit_comments_linked ADD CONSTRAINT `commit_comments_linked_pk` PRIMARY KEY (id);
ALTER TABLE commit_comments_linked ADD CONSTRAINT `commit_comments_linked_fk1` FOREIGN KEY (commit_id) REFERENCES commits_linked (id);
ALTER TABLE commit_comments_linked ADD CONSTRAINT `commit_comments_linked_fk2` FOREIGN KEY (user_id) REFERENCES GH_users (id);
DROP TABLE commit_comments;



CREATE TABLE commit_parents_linked AS
SELECT * FROM commit_parents
WHERE commit_id IN (SELECT id FROM commits_linked) OR parent_id IN (SELECT id FROM commits_linked);

ALTER TABLE commit_parents_linked ADD CONSTRAINT `commit_parents_linked_fk1` FOREIGN KEY (commit_id) REFERENCES commits_linked (id);
ALTER TABLE commit_parents_linked ADD CONSTRAINT `commit_parents_linked_fk2` FOREIGN KEY (parent_id) REFERENCES commits_linked (id);
DROP TABLE commit_parents;




CREATE TABLE tempTable1 AS SELECT id FROM commits_linked;
CREATE TABLE tempTable2 AS SELECT DISTINCT GH_project_id FROM projects_linked;

CREATE TABLE pull_requests_linked AS
SELECT * FROM pull_requests
WHERE (head_commit_id IN tempTable1 OR base_commit_id IN tempTable1) AND (head_repo_id IN tempTable2 OR base_repo_id IN tempTable2);

ALTER TABLE pull_requests_linked ADD CONSTRAINT `pull_requests_linked_pk` PRIMARY KEY (`id`);
ALTER TABLE pull_requests_linked ADD CONSTRAINT `pull_requests_linked_fk1` FOREIGN KEY (`head_repo_id`) REFERENCES projects_linked (GH_project_id);
ALTER TABLE pull_requests_linked ADD CONSTRAINT `pull_requests_linked_fk2` FOREIGN KEY (`base_repo_id`) REFERENCES projects_linked (GH_project_id);
ALTER TABLE pull_requests_linked ADD CONSTRAINT `pull_requests_linked_fk3` FOREIGN KEY (`head_commit_id`) REFERENCES commits_linked (id);
ALTER TABLE pull_requests_linked ADD CONSTRAINT `pull_requests_linked_fk4` FOREIGN KEY (`base_commit_id`) REFERENCES commits_linked (id);
DROP TABLE pull_requests;