create database credit_trans;
use credit_trans;
select * from trans_history;

describe trans_history;


-- Select COLUMN_NAME, ORDINAL_POSITION,  IS_NULLABLE, DATA_TYPE
Select *
from INFORMATION_SCHEMA.COLUMNS
where table_name = 'trans_history';

select COLUMN_NAME, ORDINAL_POSITION,  IS_NULLABLE, DATA_TYPE, COLUMN_TYPE
from INFORMATION_SCHEMA.COLUMNS
where table_name='Track';

show create table trans_history;
CREATE TABLE `trans_history` (
  `MyUnknownColumn` int DEFAULT NULL,
  `trans_date_trans_time` text,
  `cc_num` bigint DEFAULT NULL,
  `merchant` text,
  `category` text,
  `amt` double DEFAULT NULL,
  `first` text,
  `last` text,
  `gender` text,
  `street` text,
  `city` text,
  `state` text,
  `zip` int DEFAULT NULL,
  `lat` double DEFAULT NULL,
  `long` double DEFAULT NULL,
  `city_pop` int DEFAULT NULL,
  `job` text,
  `dob` text,
  `trans_num` text,
  `unix_time` int DEFAULT NULL,
  `merch_lat` double DEFAULT NULL,
  `merch_long` double DEFAULT NULL,
  `is_fraud` int DEFAULT NULL
);

select * from trans_history limit 5;

alter table trans_history drop MyUnknownColumn;


CREATE TABLE TRANSACTION_RECORDS (
    trans_num                   VARCHAR(50)     NOT NULL,
    trans_date_trans_time       DATETIME        NOT NULL,
    unix_time                   BIGINT UNSIGNED NOT NULL,
    cc_num                      VARCHAR(20)     NOT NULL,
    merchant                    VARCHAR(100)    NOT NULL,
    category                    VARCHAR(50)     NOT NULL,
    amt                         DECIMAL(10, 2)  NOT NULL,
    first                       VARCHAR(50)     NOT NULL,
    last                        VARCHAR(50)     NOT NULL,
    gender                      CHAR(1)         NOT NULL,
    dob                         DATE            NOT NULL,
    job                         VARCHAR(100)    NOT NULL,
    street                      VARCHAR(100)    NOT NULL,
    city                        VARCHAR(50)     NOT NULL,
    state                       CHAR(2)         NOT NULL,
    zip                         VARCHAR(10)     NOT NULL,
    city_pop                    INT UNSIGNED    NOT NULL,
    lat                         DECIMAL(21, 18)  NOT NULL,
    `long`                      DECIMAL(21, 18)  NOT NULL,
    merch_lat                   DECIMAL(21, 18)  NOT NULL,
    merch_long                  DECIMAL(21, 18)  NOT NULL,
    is_fraud                    TINYINT(1)      NOT NULL DEFAULT 0,
    PRIMARY KEY (trans_num)
);

drop table TRANSACTION_RECORDS;

insert into TRANSACTION_RECORDS(
	trans_num,
    trans_date_trans_time,
    unix_time,
    cc_num,
    merchant,
    category,
    amt,
    first,
    last,
    gender,
    dob,
    job,
    street,
    city,
    state,
    zip,
    city_pop,
    lat,
    `long`,
    merch_lat,
    merch_long,
    is_fraud
) 

select 
    trans_num,
    trans_date_trans_time,
    unix_time,
    cc_num,
    merchant,
    category,
    amt,
    first,
    last,
    gender,
    dob,
    job,
    street,
    city,
    state,
    zip,
    city_pop,
    lat,
    `long`,
    merch_lat,
    merch_long,
    is_fraud
from trans_history 
limit 5;

select * from trans_history limit 2;

drop table TRANSACTION_RECORDS;




