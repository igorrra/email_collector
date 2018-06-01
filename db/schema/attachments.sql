-- Schema for `attachments` table

CREATE TABLE IF NOT EXISTS `email_collector`.`attachments` (
	`id`	INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
	`md5`	CHAR(32) NOT NULL COMMENT 'Email\'s MD5 sum',
	`path`	VARCHAR(64) COMMENT 'Path to the saved attachment on NFS',
	PRIMARY KEY (`id`),
	UNIQUE KEY (`md5`),
	UNIQUE KEY (`path`),
	INDEX `path_idx` (`path` ASC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;