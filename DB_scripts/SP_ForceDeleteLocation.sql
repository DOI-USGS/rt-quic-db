CREATE DEFINER=`quicdbadmin`@`%` PROCEDURE `ForceDeleteLocation`(IN ID INT)
BEGIN    
	DELETE FROM LocAffiliatedWithUser
	WHERE loc_ID = ID;
    
    DELETE FROM Location
    WHERE loc_ID = ID;

END