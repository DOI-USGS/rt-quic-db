INSERT INTO `rt_quic_db`.`Users` (`NAME`, `ROLE`, `USERNAME`, `PASSWORD`) VALUES ('Chit', 'admin', 'chit', 'chit');
INSERT INTO `rt_quic_db`.`Users` (`NAME`, `ROLE`, `USERNAME`, `PASSWORD`) VALUES ('Nathan', 'admin', 'nathan', 'nathan');
INSERT INTO `rt_quic_db`.`Users` (`NAME`, `ROLE`, `USERNAME`, `PASSWORD`) VALUES ('Jojo', 'admin', 'jojo', 'jojo');

INSERT INTO `rt_quic_db`.`Plate` (`plate_ID`, `plate_type`, `other_plate_attr`) VALUES (99, 'Test_Plate', NULL)
INSERT INTO `rt_quic_db`.`Sample` (`sample_ID`, `name`, `species`, `sex`, `age`, `tissue_matrix`, `other_sample_attr`) 
	VALUES (99, 'Test_Sample', 'Bovine', 'F', 5, 'CSF', NULL);
INSERT INTO `rt_quic_db`.`Location` (`loc_ID`, `name`) VALUES (99, 'Test_Location')