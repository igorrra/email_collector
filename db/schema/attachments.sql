-- Schema for `attachments` table

CREATE TABLE IF NOT EXISTS `email_collector`.`attachments` (
	`id`			INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
	`attachment_name` 			VARCHAR(255) NOT NULL COMMENT 'Attachment name',
	`attachment_size` 			INT(10) NOT NULL COMMENT 'Attachment size in bytes',
	`content_type` 		VARCHAR(127) NOT NULL COMMENT 'Attachment content type',
	`md5`			CHAR(32) NOT NULL COMMENT 'Email\'s MD5 sum',
	`path`			NVARCHAR(260) COMMENT 'Path to the saved attachment on NFS',
	`metadata_id` 		INT(10) UNSIGNED NOT NULL COMMENT 'Metadata id',
	PRIMARY KEY (`id`),
	FOREIGN KEY (`metadata_id`) REFERENCES `email_collector`.`metadata` (`id`) ON DELETE CASCADE,
	INDEX `path_idx` (`path` ASC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;