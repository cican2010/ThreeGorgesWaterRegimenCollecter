/*
 Navicat Premium Data Transfer

 Source Server         : localhost
 Source Server Type    : MySQL
 Source Server Version : 50723
 Source Host           : localhost:3306
 Source Schema         : three_gorges_water_regimen

 Target Server Type    : MySQL
 Target Server Version : 50723
 File Encoding         : 65001

 Date: 02/03/2019 13:35:21
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for water_regimen
-- ----------------------------
DROP TABLE IF EXISTS `water_regimen`;
CREATE TABLE `water_regimen`  (
  `id` int(255) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'id',
  `date` date NOT NULL COMMENT '日期',
  `hour` int(4) NULL DEFAULT NULL COMMENT '时刻',
  `site` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '站点名称',
  `upLevel` double(10, 2) NULL DEFAULT NULL COMMENT '上游水位',
  `downLevel` double(10, 2) NULL DEFAULT NULL COMMENT '下游水位',
  `inSpeed` double(10, 4) NULL DEFAULT NULL COMMENT '进站流量',
  `outSpeed` double(10, 4) NULL DEFAULT NULL COMMENT '出站流量',
  `created_at` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0) COMMENT '创建时间',
  `updated_at` datetime(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0) COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `date_hour_site`(`date`, `hour`, `site`) USING BTREE COMMENT '同一站点同一时刻只能有同一行数据'
) ENGINE = InnoDB AUTO_INCREMENT = 1900 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
