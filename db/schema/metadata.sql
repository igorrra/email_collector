-- Schema for `metadata` table

CREATE TABLE IF NOT EXISTS `email_collector`.`metadata` (
	`id`				INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
	`sender`			VARCHAR(256) NOT NULL COMMENT 'The sender of the email data object',
	`subject`			VARCHAR(256) COMMENT 'The subject of the email data object',
	`body`				TEXT COMMENT 'Body of the email data object',
	`html`				TEXT COMMENT 'Body of the email data object (HTML formatted)',
	`timestamp`			TIMESTAMP NOT NULL COMMENT 'Timestamp that message was received at',
	PRIMARY KEY (`id`),
	INDEX `sender_idx` (`sender` ASC),
	INDEX `subject_idx` (`subject` ASC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;