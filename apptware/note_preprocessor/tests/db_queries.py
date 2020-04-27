CREATE_ORGANIZATION_QUERY = """
CREATE TABLE `Organization` (
  `OrgID` varchar(10) NOT NULL,
  `Name` varchar(100) DEFAULT NULL,
  `TimeZoneName` varchar(64) NOT NULL COMMENT 'Time zone name as defined by https://www.iana.org/time-zones. Note that in general these should work with any standard time zone conversion functions including Java 9, MySQL, etc.',
  `UpdateDate` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `UpdateSource` varchar(20) NOT NULL,
  PRIMARY KEY (`OrgID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='An organization that DS supports. This is typically a hospital system that consists of one or more physical locations or facilities.';
"""

LOAD_DATA_QUERY = """
    LOAD DATA LOCAL INFILE 'fixtures/data-files/{table_name}.csv' 
    INTO TABLE {table_name}
    FIELDS TERMINATED BY ','
    ENCLOSED BY '\"'
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS;
"""

CREATE_PROVIDER_TYPE_QUERY = """
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
"""

CREATE_PHYSICIANNOTE_QUERY = """
CREATE TABLE `STG_PIECES_physiciannote` (
  `PhysicianNoteRowID` int(11) NOT NULL AUTO_INCREMENT,
  `HospitalCode` varchar(20) NOT NULL,
  `PatientID` varchar(20) NOT NULL,
  `EncounterID` varchar(20) NOT NULL,
  `NoteID` varchar(20) NOT NULL,
  `NoteType` varchar(6) NOT NULL,
  `NoteProviderID` varchar(20) NOT NULL,
  `NoteDate` datetime NOT NULL,
  `NoteStatus` varchar(20) DEFAULT NULL,
  `NoteText` longtext NOT NULL,
  `AddDate` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `AddSource` varchar(20) NOT NULL,
  `UpdateDate` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `UpdateSource` varchar(20) NOT NULL,
  PRIMARY KEY (`PatientID`,`EncounterID`,`HospitalCode`,`NoteID`),
  UNIQUE KEY `PhysicianNoteRowID` (`PhysicianNoteRowID`),
  KEY `UpdateDate` (`UpdateDate`)
) ENGINE=InnoDB AUTO_INCREMENT=3151 DEFAULT CHARSET=utf8;
"""

CREATE_PHYSIANNOTE_PROPERTIES_QUERY = """
CREATE TABLE `physiciannote_properties` (
  `HospitalCode` varchar(20) NOT NULL,
  `PatientID` varchar(20) NOT NULL,
  `EncounterID` varchar(20) NOT NULL,
  `NoteID` varchar(20) NOT NULL,
  `RawNoteType` varchar(100) DEFAULT NULL COMMENT 'original type sent by the customer',
  `NoteAuthorType` varchar(100) DEFAULT NULL COMMENT 'Identifies the provider type for the note author.  These types are specific to each hospital. Use pieces_common.provider_type(org_id, code) to get additional details, pieces_common.provider_type_group for grouping.',
  PRIMARY KEY (`PatientID`,`EncounterID`,`HospitalCode`,`NoteID`) COMMENT 'shared primary key with physiciannote table.  This is not actually keyed to physiciannote due to low visibility into the processes feeding that table, but a foreign key could be warranted',
  KEY `RawNoteType` (`RawNoteType`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='detail table for additional properties of text fields';
"""
