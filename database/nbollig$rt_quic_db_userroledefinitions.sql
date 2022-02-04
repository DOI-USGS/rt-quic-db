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
-- Table structure for table `userroledefinitions`
--

DROP TABLE IF EXISTS `userroledefinitions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `userroledefinitions` (
  `security_point_ID` int NOT NULL,
  `user_role_ID` int NOT NULL,
  PRIMARY KEY (`security_point_ID`,`user_role_ID`),
  KEY `fk_UserRoleDefinitions_C_User_Roles_idx` (`user_role_ID`),
  CONSTRAINT `fk_UserRoleDefinitions_C_Security_Points` FOREIGN KEY (`security_point_ID`) REFERENCES `c_security_points` (`ID`),
  CONSTRAINT `fk_UserRoleDefinitions_C_User_Roles` FOREIGN KEY (`user_role_ID`) REFERENCES `c_user_roles` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `userroledefinitions`
--

LOCK TABLES `userroledefinitions` WRITE;
/*!40000 ALTER TABLE `userroledefinitions` DISABLE KEYS */;
INSERT INTO `userroledefinitions` VALUES (100,1),(100,2),(110,2),(115,2),(120,2),(140,2),(160,2),(200,2),(210,2),(220,2),(240,2),(100,3),(110,3),(115,3),(130,3),(150,3),(170,3),(200,3),(210,3),(230,3),(250,3),(800,11),(810,11),(800,12),(810,12),(820,12),(830,12),(500,13),(510,13),(520,13),(530,13),(600,13),(610,13),(620,13),(630,13),(700,13),(720,13),(730,13),(800,13),(810,13),(820,13),(830,13),(840,13);
/*!40000 ALTER TABLE `userroledefinitions` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-02-04 12:35:59
