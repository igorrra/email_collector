-- Schema for `metadata` table

CREATE TABLE metadata (
	`id`				INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
	`sender`			VARCHAR(30) COMMENT 'The sender of the email data object',
	`recepient`			VARCHAR(30) NOT NULL COMMENT 'The recipient(s) of the email data object',
	`subject`			VARCHAR(30) COMMENT 'The subject of the email data object',
	`body`				TEXT COMMENT 'Body of the email data object',
	`datetime`			DATETIME NOT NULL COMMENT 'Date and time the message was received (YYYY-MM-DD HH:MM:SS)',
	`attachment_id`			INT(10) UNSIGNED COMMENT 'The id of attachment(s) if any',
	PRIMARY KEY (id),
	FOREIGN KEY (attachment_id) REFERENCES attachments(id),
	INDEX `sender` (sender),
	INDEX `recepient` (recepient),
	INDEX `subject` (subject)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;