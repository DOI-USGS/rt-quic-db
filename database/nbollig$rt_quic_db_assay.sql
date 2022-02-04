-- MySQL dump 10.13  Distrib 8.0.26, for Win64 (x86_64)
--
-- Host: localhost    Database: nbollig$rt_quic_db
-- ------------------------------------------------------
-- Server version	8.0.27

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `assay`
--

DROP TABLE IF EXISTS `assay`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assay` (
  `assay_ID` int NOT NULL AUTO_INCREMENT,
  `temperature` decimal(6,2) DEFAULT NULL,
  `shake_interval_min` decimal(8,3) DEFAULT NULL,
  `scan_interval_min` decimal(8,3) DEFAULT NULL,
  `duration_min` decimal(8,3) DEFAULT NULL,
  `salt_type` varchar(45) DEFAULT NULL,
  `salt_conc` varchar(45) DEFAULT NULL,
  `substrate_type` varchar(45) DEFAULT NULL,
  `substrate_conc` varchar(45) DEFAULT NULL,
  `surfact_type` varchar(45) DEFAULT NULL,
  `surfact_conc` varchar(45) DEFAULT NULL,
  `start_date_time` datetime DEFAULT NULL,
  `other_assay_attr` varchar(45) DEFAULT NULL,
  `loc_ID` int DEFAULT NULL,
  `name` varchar(45) DEFAULT NULL,
  `plate_ID` int DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  `team_ID` int DEFAULT NULL,
  PRIMARY KEY (`assay_ID`),
  KEY `loc_ID_idx` (`loc_ID`),
  KEY `fk_Assay_Plate_idx` (`plate_ID`),
  KEY `fk_Assay_Users_idx` (`created_by`),
  KEY `fk_Assay_Team_idx` (`team_ID`),
  CONSTRAINT `fk_Assay_Location` FOREIGN KEY (`loc_ID`) REFERENCES `location` (`loc_ID`) ON UPDATE CASCADE,
  CONSTRAINT `fk_Assay_Plate` FOREIGN KEY (`plate_ID`) REFERENCES `plate` (`plate_ID`),
  CONSTRAINT `fk_Assay_Team` FOREIGN KEY (`team_ID`) REFERENCES `team` (`team_ID`),
  CONSTRAINT `fk_Assay_Users` FOREIGN KEY (`created_by`) REFERENCES `users` (`ID`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=954 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-02-04 12:32:06
