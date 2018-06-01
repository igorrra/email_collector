-- Schema for `recepients` table

CREATE TABLE recepients (
	`id`		INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
	`email`		VARCHAR(256) NOT NULL COMMENT 'Recepient\'s email',
	PRIMARY KEY (id),
	INDEX `email` (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
