-- Schema for `metadata_attachments` table

CREATE TABLE IF NOT EXISTS `email_collector`.`metadata_attachments` (
	`id`				INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
	`metadata_id`			INT(10) UNSIGNED NOT NULL COMMENT 'Metadata id',
	`attachment_id`			INT(10) UNSIGNED NOT NULL COMMENT 'Attachment id',
	PRIMARY KEY (`id`),
	FOREIGN KEY (`metadata_id`) REFERENCES metadata(`id`),
	FOREIGN KEY (`attachment_id`) REFERENCES attachments(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
