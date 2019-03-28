-- create indeces on the 2 columns that the join will happen on
CREATE INDEX 'repo_GH' ON `projects` (url);
CREATE INDEX 'repo_SO' ON `PostReferenceGH` (Repo);


-- create master table containing the PK's and important FK's of the 2 tables to be joined
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


-- run select statement for joining the 2 tables, then get the results and put them into the master table
INSERT INTO Master_repo_linkage
SELECT PostReferenceGH.PostId, PostReferenceGH.Id, projects.id, projects.owner_id, PostReferenceGH.Repo
  FROM PostReferenceGH, projects
 WHERE PostReferenceGH.Repo = projects.url;
 
 
 -- create second linkage table (that will not contain PostReferenceGH ids)
 CREATE TABLE `Master_linkage` (
  `SO_post_id` INT NOT NULL,
  `GH_project_id` INT(11) NOT NULL,
  `GH_owner_id` INT(11) NULL DEFAULT NULL,
  `GH_repoName` VARCHAR(255) NOT NULL,
  CONSTRAINT `master2_pk` PRIMARY KEY (`SO_post_id`,`GH_project_id`),
  CONSTRAINT `master2_fk_1` FOREIGN KEY(`SO_post_id`) REFERENCES Posts(Id),
  CONSTRAINT `master2_fk_2` FOREIGN KEY(`GH_project_id`) REFERENCES projects(id),
  CONSTRAINT `master2_fk_3` FOREIGN KEY(`GH_owner_id`) REFERENCES GH_users(id) )
ENGINE = "MyISAM"
DEFAULT CHARACTER SET = utf8;


-- insert all distinct values of the linkage inside this new master-linkage table
INSERT INTO Master_linkage SELECT DISTINCT SO_post_id, GH_project_id, GH_owner_id, GH_repoName FROM Master_repo_linkage;
 

-- create indeces on the ppk's of the master table
CREATE INDEX Master_Linkage_ppk_SO ON Master_linkage(SO_post_id);
CREATE INDEX Master_Linkage_ppk_GH ON Master_linkage(GH_project_id);