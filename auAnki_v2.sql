drop table if exists has;
drop table if exists Voclist;
drop table if exists User;
drop table if exists Subtitle;
drop table if exists Video;



create table Video(
vid integer(11) NOT NULL AUTO_INCREMENT,
vname varchar(50) NOT NULL,
lang varchar(10) NOT NULL,
season integer(5),
episode integer(5),
adjusttime integer(6) NOT NULL DEFAULT 0,
vfilename varchar(50),
PRIMARY KEY (vid)
);


create table Subtitle(
sid bigint NOT NULL AUTO_INCREMENT,
sstime TIME,
sftime TIME,
org varchar(1024),
translation varchar(1024),
vid integer(11) NOT NULL,
PRIMARY KEY (sid),
FOREIGN KEY (vid) REFERENCES Video(vid) ON DELETE CASCADE
);

create table `User`(
uid integer(11) NOT NULL AUTO_INCREMENT,
userid varchar(50) NOT NULL,
PRIMARY KEY (uid)
);

create table Voclist(
uid integer(11) NOT NULL,
vocid integer(11) NOT NULL,
vname varchar(50) NOT NULL,
PRIMARY KEY (uid,vocid),
FOREIGN KEY (uid) REFERENCES User(uid) ON DELETE CASCADE
);

create table has(
uid integer(11) NOT NULL,
vocid integer(11) NOT NULL,
sid bigint NOT NULL,
tag varchar(50),
PRIMARY KEY (uid,vocid,sid),
FOREIGN KEY (uid,vocid) REFERENCES `Voclist`(uid,vocid) ON DELETE CASCADE,
FOREIGN KEY (sid) REFERENCES `Subtitle`(sid) ON DELETE CASCADE
);

-- Insert into `User` values (1,'Jason');
INSERT INTO `User` (`userid`) VALUES
('zdadadaz');

-- INSERT INTO `Video` (`vname`,`lang`,`season`,`episode`) VALUES
-- ('夏目友人帳','jp',4,1),
-- ('Big bang theory','en',8,1);
