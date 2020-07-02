-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema rt_quic_db
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema rt_quic_db
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `rt_quic_db` ;
USE `rt_quic_db` ;

-- -----------------------------------------------------
-- Table `rt_quic_db`.`Plate`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `rt_quic_db`.`Plate` (
  `plate_ID` INT NOT NULL,
  `plate_type` VARCHAR(45) NOT NULL,
  `other_plate_attr` VARCHAR(45) NULL,
  PRIMARY KEY (`plate_ID`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rt_quic_db`.`Sample`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `rt_quic_db`.`Sample` (
  `sample_ID` INT NOT NULL,
  `species` VARCHAR(45) NULL,
  `sex` VARCHAR(45) NULL,
  `age` VARCHAR(45) NULL,
  `tissue_matrix` VARCHAR(45) NULL,
  `other_sample_attr` VARCHAR(45) NULL,
  PRIMARY KEY (`sample_ID`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rt_quic_db`.`Location`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `rt_quic_db`.`Location` (
  `loc_ID` INT NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`loc_ID`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rt_quic_db`.`Assay`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `rt_quic_db`.`Assay` (
  `assay_ID` INT NOT NULL,
  `temperature` DECIMAL(6,2) NULL,
  `shake_interval_min` DECIMAL(8,3) NULL,
  `scan_interval_min` DECIMAL(8,3) NULL,
  `duration_min` DECIMAL(8,3) NULL,
  `salt_type` VARCHAR(45) NULL,
  `salt_conc` VARCHAR(45) NULL,
  `substrate_type` VARCHAR(45) NULL,
  `substrate_conc` VARCHAR(45) NULL,
  `surfact_type` VARCHAR(45) NULL,
  `surfact_conc` VARCHAR(45) NULL,
  `start_date_time` DATETIME NULL,
  `other_assay_attr` VARCHAR(45) NULL,
  `sample_ID` INT NULL,
  `loc_ID` INT NULL,
  PRIMARY KEY (`assay_ID`),
  INDEX `sample_ID_idx` (`sample_ID` ASC),
  INDEX `loc_ID_idx` (`loc_ID` ASC),
  CONSTRAINT `fk_Assay_Sample`
    FOREIGN KEY (`sample_ID`)
    REFERENCES `rt_quic_db`.`Sample` (`sample_ID`)
    ON DELETE NO ACTION
    ON UPDATE CASCADE,
  CONSTRAINT `fk_Assay_Location`
    FOREIGN KEY (`loc_ID`)
    REFERENCES `rt_quic_db`.`Location` (`loc_ID`)
    ON DELETE NO ACTION
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rt_quic_db`.`Well_Condition`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `rt_quic_db`.`Well_Condition` (
  `wc_ID` INT NOT NULL,
  `salt_type` VARCHAR(45) NULL,
  `salt_conc` VARCHAR(45) NULL,
  `substrate_type` VARCHAR(45) NULL,
  `substrate_conc` VARCHAR(45) NULL,
  `surfact_type` VARCHAR(45) NULL,
  `surfact_conc` VARCHAR(45) NULL,
  `other_wc_attr` VARCHAR(45) NULL,
  `sample_ID` INT NULL,
  `assay_ID` INT NOT NULL,
  PRIMARY KEY (`wc_ID`),
  INDEX `sample_ID_idx` (`sample_ID` ASC),
  INDEX `assay_ID_idx` (`assay_ID` ASC),
  CONSTRAINT `fk_Well_Condition_Sample`
    FOREIGN KEY (`sample_ID`)
    REFERENCES `rt_quic_db`.`Sample` (`sample_ID`)
    ON DELETE NO ACTION
    ON UPDATE CASCADE,
  CONSTRAINT `fk_Well_Condition_Assay`
    FOREIGN KEY (`assay_ID`)
    REFERENCES `rt_quic_db`.`Assay` (`assay_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rt_quic_db`.`Observation`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `rt_quic_db`.`Observation` (
  `obs_ID` INT NOT NULL,
  `fluorescence` DECIMAL(20,4) NULL,
  `date_time` DATETIME NULL,
  `x_coord` INT NOT NULL,
  `y_coord` INT NOT NULL,
  `plate_ID` INT NOT NULL,
  `wc_ID` INT NOT NULL,
  PRIMARY KEY (`obs_ID`),
  INDEX `plate_ID_idx` (`plate_ID` ASC),
  INDEX `wc_ID_idx` (`wc_ID` ASC),
  CONSTRAINT `fk_Observation_Plate`
    FOREIGN KEY (`plate_ID`)
    REFERENCES `rt_quic_db`.`Plate` (`plate_ID`)
    ON DELETE NO ACTION
    ON UPDATE CASCADE,
  CONSTRAINT `fk_Observation_Well_Condition`
    FOREIGN KEY (`wc_ID`)
    REFERENCES `rt_quic_db`.`Well_Condition` (`wc_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rt_quic_db`.`Users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `rt_quic_db`.`Users` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `name` CHAR(50) NULL,
  `role` CHAR(30) NULL,
  `username` CHAR(50) NOT NULL,
  `password` CHAR(50) NULL,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rt_quic_db`.`LocAffiliatedWithUser`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `rt_quic_db`.`LocAffiliatedWithUser` (
  `loc_ID` INT NOT NULL,
  `user_ID` INT NOT NULL,
  PRIMARY KEY (`loc_ID`, `user_ID`),
  INDEX `ID_idx` (`user_ID` ASC),
  CONSTRAINT `fk_Location`
    FOREIGN KEY (`loc_ID`)
    REFERENCES `rt_quic_db`.`Location` (`loc_ID`)
    ON DELETE NO ACTION
    ON UPDATE CASCADE,
  CONSTRAINT `fk_User`
    FOREIGN KEY (`user_ID`)
    REFERENCES `rt_quic_db`.`Users` (`ID`)
    ON DELETE NO ACTION
    ON UPDATE CASCADE)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

-- -----------------------------------------------------
-- Additional Updates
-- -----------------------------------------------------


ALTER TABLE Sample ADD
		`name` VARCHAR(45) NULL;

ALTER TABLE Assay ADD
		`name` VARCHAR(45) NULL;

		
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
ALTER TABLE Assay MODIFY COLUMN `assay_ID` INT NOT NULL AUTO_INCREMENT;
ALTER TABLE Well_Condition MODIFY COLUMN `wc_ID` INT NOT NULL AUTO_INCREMENT;
ALTER TABLE Sample MODIFY COLUMN `sample_ID` INT NOT NULL AUTO_INCREMENT;
ALTER TABLE Location MODIFY COLUMN `loc_ID` INT NOT NULL AUTO_INCREMENT;
ALTER TABLE Observation MODIFY COLUMN `obs_ID` INT NOT NULL AUTO_INCREMENT;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS

ALTER TABLE `Well_Condition` ADD
		`well_name` VARCHAR(45) NULL;
ALTER TABLE `Well_Condition` ADD
		`contents` VARCHAR(45) NULL;

ALTER TABLE Observation CHANGE COLUMN `date_time` `time_s` DECIMAL(20,3);
ALTER TABLE Observation ADD
		`index_in_well` INT NULL;
		

ALTER TABLE `LocAffiliatedWithUser` DROP FOREIGN KEY `fk_User`; 
ALTER TABLE `LocAffiliatedWithUser`  
ADD CONSTRAINT `fk_User` 
    FOREIGN KEY (`user_id`) REFERENCES `Users` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE;