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

