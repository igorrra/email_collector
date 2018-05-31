-- Schema for `attachments` table

CREATE TABLE attachments (
	`id`	INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
	`md5`	CHAR(32) NOT NULL COMMENT 'Email\'s MD5 sum',
	`path`	VARCHAR(30) COMMENT 'Path to the saved attachment on NFS',
	PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;