-- Schema for `recipients` table

CREATE TABLE IF NOT EXISTS `email_collector`.`recipients` (
	`id`		INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
	`email`		VARCHAR(256) NOT NULL COMMENT 'Recepient\'s email',
	PRIMARY KEY (`id`),
	INDEX `email_idx` (`email` ASC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;