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
-- Table structure for table `well_condition`
--

DROP TABLE IF EXISTS `well_condition`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `well_condition` (
  `wc_ID` int NOT NULL AUTO_INCREMENT,
  `salt_type` varchar(45) DEFAULT NULL,
  `salt_conc` varchar(45) DEFAULT NULL,
  `substrate_type` varchar(45) DEFAULT NULL,
  `substrate_conc` varchar(45) DEFAULT NULL,
  `surfact_type` varchar(45) DEFAULT NULL,
  `surfact_conc` varchar(45) DEFAULT NULL,
  `other_wc_attr` varchar(45) DEFAULT NULL,
  `sample_ID` int DEFAULT NULL,
  `assay_ID` int NOT NULL,
  `contents` varchar(45) DEFAULT NULL,
  `well_name` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`wc_ID`),
  KEY `sample_ID_idx` (`sample_ID`),
  KEY `assay_ID_idx` (`assay_ID`),
  CONSTRAINT `fk_Well_Condition_Assay` FOREIGN KEY (`assay_ID`) REFERENCES `assay` (`assay_ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_Well_Condition_Sample` FOREIGN KEY (`sample_ID`) REFERENCES `sample` (`sample_ID`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5181 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-02-04 12:32:07
