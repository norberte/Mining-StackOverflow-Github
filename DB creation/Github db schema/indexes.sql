CREATE UNIQUE INDEX `login` ON `GH_users` (`login` ASC)  COMMENT '';
CREATE UNIQUE INDEX `sha` ON `commits` (`sha` ASC)  COMMENT '';
CREATE UNIQUE INDEX `comment_id` ON `commit_comments` (`comment_id` ASC)  COMMENT '';
CREATE INDEX `follower_id` ON `followers` (`follower_id` ASC) COMMENT '';
CREATE UNIQUE INDEX `pullreq_id` ON `pull_requests` (`pullreq_id` ASC, `base_repo_id` ASC)  COMMENT '';
CREATE INDEX `name` ON `projects` (`name` ASC)  COMMENT '';
CREATE INDEX `commit_id` ON `project_commits` (`commit_id` ASC)  COMMENT '';
CREATE INDEX `project_id` ON `project_languages` (`project_id`) COMMENT '';


CREATE INDEX 'repo_GH' ON `projects` (url);
CREATE INDEX 'repo_SO' ON `PostReferenceGH` (Repo);


CREATE TABLE `Master_repo_linkage` (
  `SO_post_id` INT NOT NULL,
  `SO_postRefGH_id` INT NOT NULL,
  `GH_project_id` INT(11) NOT NULL,
  `GH_owner_id` INT(11) NULL DEFAULT NULL,
  `GH_repoName` VARCHAR(255) NOT NULL,
  CONSTRAINT `master_pk` PRIMARY KEY (`SO_postRefGH_id`,`GH_project_id`),
  CONSTRAINT `master_fk_1` FOREIGN KEY(`SO_post_id`) REFERENCES Posts(Id),
  CONSTRAINT `master_fk_2` FOREIGN KEY(`SO_postRefGH_id`) REFERENCES PostReferenceGH(Id),
  CONSTRAINT `master_fk_3` FOREIGN KEY(`GH_project_id`) REFERENCES projects(id),
  CONSTRAINT `master_fk_4` FOREIGN KEY(`GH_owner_id`) REFERENCES GH_users(id) )
ENGINE = "MyISAM"
DEFAULT CHARACTER SET = utf8;


INSERT INTO Master_repo_linkage
SELECT PostReferenceGH.PostId, PostReferenceGH.Id, projects.id, projects.owner_id, PostReferenceGH.Repo
  FROM PostReferenceGH, projects
 WHERE PostReferenceGH.Repo = projects.url;


CREATE INDEX 'Master_repoLinkage_ppk_SO' ON `Master_repo_linkage` (SO_postRefGH_id);
CREATE INDEX 'Master_repoLinkage_ppk_GH' ON `Master_repo_linkage` (GH_project_id);