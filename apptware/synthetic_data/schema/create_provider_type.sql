CREATE TABLE `provider_type` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'Auto-generated primary key',
  `org_id` varchar(10) NOT NULL COMMENT 'The organization to which this provider type applies',
  `code` varchar(100) NOT NULL COMMENT 'A short code representing the provider type.  This is typically the value received from the client organization.',
  `name` varchar(100) NOT NULL COMMENT 'The common name for the provider type',
  `description` varchar(255) DEFAULT NULL COMMENT 'A more detailed description for the provider type',
  `update_date` datetime(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT 'The date/time this record was created or last updated (based on the database server clock)',
  `update_source` varchar(20) NOT NULL COMMENT 'The identity of the person or process that last updated this record',
  PRIMARY KEY (`id`),
  UNIQUE KEY `provider_type_org_id_code` (`org_id`,`code`),
  CONSTRAINT `provider_type_ibfk_1` FOREIGN KEY (`org_id`) REFERENCES `Organization` (`OrgID`)
) ENGINE=InnoDB AUTO_INCREMENT=255 DEFAULT CHARSET=utf8 COMMENT='A ''provider type'' as used within a client organization.  Typically these represent ''Physician'', ''Nurse'', ''Case manager'', etc.';
