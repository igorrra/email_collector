CREATE DATABASE IF NOT EXISTS `email_collector` DEFAULT CHARACTER SET utf8;
USE `email_collector`;
source schema/attachments.sql
source schema/metadata.sql
source schema/metadata_attachments.sql
source schema/recipients.sql
source schema/metadata_recipients.sql