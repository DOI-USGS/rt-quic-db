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
-- Table structure for table `c_security_points`
--

DROP TABLE IF EXISTS `c_security_points`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `c_security_points` (
  `ID` int NOT NULL,
  `name` varchar(200) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `c_security_points`
--

LOCK TABLES `c_security_points` WRITE;
/*!40000 ALTER TABLE `c_security_points` DISABLE KEYS */;
INSERT INTO `c_security_points` VALUES (100,'Can access View Assay activity'),(110,'Upload assays'),(115,'Can access Edit Assay activity'),(120,'Edit only assays created by self'),(130,'Edit all assays'),(140,'Delete only assays created by self'),(150,'Delete all assays'),(160,'Well edit only assays created by self'),(170,'Well edit all assays'),(200,'Can access Manage Samples activity'),(210,'Create samples'),(220,'Edit only samples created by self'),(230,'Edit all samples'),(240,'Delete only samples created by self'),(250,'Delete all samples'),(500,'Can access Manage Plate Templates activity'),(510,'Create plate templates'),(520,'Edit plate templates'),(530,'Delete plate templates'),(600,'Can access Manage Locations activity'),(610,'Create new locations for your team'),(620,'Update location in your team'),(630,'Delete location in your team'),(700,'Can access Manage Team activity'),(720,'Update research team settings'),(730,'Can delete a research team'),(800,'Can access Manage Users activity'),(810,'Can activate new and inactive users'),(820,'Can inactivate users'),(830,'Can modify non-admin security points of any user'),(840,'Can modify admin security points of any user'),(850,'Can delete a user'),(900,'May access data designated by any research team for analytics');
/*!40000 ALTER TABLE `c_security_points` ENABLE KEYS */;
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
