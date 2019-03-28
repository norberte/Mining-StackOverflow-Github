---- stitching together Master Linkage and projects (GH) table
CREATE TABLE projects_linked AS
SELECT Master_linkage.*, projects.*
FROM Master_linkage LEFT JOIN projects ON Master_linkage.GH_project_id = projects.id
ORDER BY Master_linkage.GH_project_id;

-- adding all the PPKs and FKs to the newly stitched table
ALTER TABLE projects_linked ADD CONSTRAINT `projects_linked_pk` PRIMARY KEY (GH_project_id, SO_post_id);
ALTER TABLE projects_linked ADD CONSTRAINT `projects_linked_fk_1` FOREIGN KEY (`SO_post_id`) REFERENCES Posts(Id);  -- failed to run
ALTER TABLE projects_linked ADD CONSTRAINT `projects_linked_fk_2` FOREIGN KEY (`owner_id`) REFERENCES GH_users(id);
ALTER TABLE projects_linked ADD CONSTRAINT `projects_linked_fk_3` FOREIGN KEY (`forked_from`) REFERENCES projects(id);  -- failed to run


---- stitching together Master Linkage and Posts (SO) table
CREATE TABLE Posts_linked AS
SELECT Master_linkage.*, Posts.*
FROM Master_linkage LEFT JOIN Posts ON Master_linkage.SO_post_id = Posts.Id
ORDER BY Master_linkage.SO_post_id;

-- adding all the PPKs and FKs to the newly stitched table
ALTER TABLE Posts_linked ADD CONSTRAINT `Posts_linked_ppk` PRIMARY KEY (GH_project_id, SO_post_id);
ALTER TABLE Posts_linked ADD CONSTRAINT `Posts_linked_fk1` FOREIGN KEY (AcceptedAnswerId) REFERENCES Posts(Id);
ALTER TABLE Posts_linked ADD CONSTRAINT `Posts_linked_fk2` FOREIGN KEY (ParentId) REFERENCES Posts(Id);
ALTER TABLE Posts_linked ADD CONSTRAINT `Posts_linked_fk3` FOREIGN KEY (PostTypeId) REFERENCES PostType(Id);
ALTER TABLE Posts_linked ADD CONSTRAINT `Posts_linked_fk4` FOREIGN KEY (GH_project_id) REFERENCES projects(id);  -- failed to run
ALTER TABLE Posts_linked ADD CONSTRAINT `Posts_linked_fk5` FOREIGN KEY (GH_owner_id) REFERENCES GH_users(id);