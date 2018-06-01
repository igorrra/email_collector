-- Schema for `metadata` table

CREATE TABLE metadata (
	`id`				INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
	`sender`			VARCHAR(256) NOT NULL COMMENT 'The sender of the email data object',
	`subject`			VARCHAR(256) COMMENT 'The subject of the email data object',
	`body`				TEXT COMMENT 'Body of the email data object',
	`timestamp`			TIMESTAMP NOT NULL COMMENT 'Timestamp that message was received at',
	PRIMARY KEY (id),
	INDEX `sender` (sender),
	INDEX `subject` (subject)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;