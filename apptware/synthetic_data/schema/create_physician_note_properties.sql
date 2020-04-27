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

