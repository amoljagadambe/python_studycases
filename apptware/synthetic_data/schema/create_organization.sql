CREATE TABLE `Organization` (
  `OrgID` varchar(10) NOT NULL,
  `Name` varchar(100) DEFAULT NULL,
  `TimeZoneName` varchar(64) NOT NULL COMMENT 'Time zone name as defined by https://www.iana.org/time-zones. Note that in general these should work with any standard time zone conversion functions including Java 9, MySQL, etc.',
  `UpdateDate` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `UpdateSource` varchar(20) NOT NULL,
  PRIMARY KEY (`OrgID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='An organization that DS supports. This is typically a hospital system that consists of one or more physical locations or facilities.';
