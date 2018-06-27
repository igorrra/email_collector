CREATE DATABASE IF NOT EXISTS `email_collector` DEFAULT CHARACTER SET utf8;
USE `email_collector`;
source schema/metadata.sql
source schema/attachments.sql
source schema/recipients.sql