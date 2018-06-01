-- Schema for `metadata_recipients` table

CREATE TABLE IF NOT EXISTS `email_collector`.`metadata_recipients` (
	`id`				INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
	`metadata_id`			INT(10) UNSIGNED NOT NULL COMMENT 'Metadata id',
	`recipient_id`			INT(10) UNSIGNED NOT NULL COMMENT 'Recipient id',
	PRIMARY KEY (`id`),
	FOREIGN KEY (`metadata_id`) REFERENCES metadata(`id`),
	FOREIGN KEY (`recipient_id`) REFERENCES recipients(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;