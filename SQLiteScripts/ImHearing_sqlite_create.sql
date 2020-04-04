CREATE TABLE ArchiveTable (
	archive_id           varchar(255) NOT NULL  PRIMARY KEY  ,
	archive_creation_date datetime     ,
	path                 varchar(255)     ,
	uploaded             boolean
 );

CREATE TABLE RecordTable (
	record_id            varchar(255) NOT NULL    ,
	record_date          date     ,
	record_start         datetime     ,
	record_end           datetime     ,
	record_size          bigint     ,
	uploaded             varchar(100)     ,
	path                 varchar(255)     ,
	CONSTRAINT Unq_RecordTable_record_id UNIQUE ( record_id )
 );

CREATE INDEX Idx_record_start ON RecordTable ( record_start );

CREATE INDEX Idx_record_date ON RecordTable ( record_date );

CREATE TABLE UserTable (
	user_id              bigint NOT NULL    ,
	user_name            varchar(100) NOT NULL    ,
	user_email           varchar(100)     ,
	user_pass            varchar(100) NOT NULL    ,
	user_lastlogin       datetime
 );

CREATE INDEX Idx_user_id ON UserTable ( user_id );

CREATE TABLE RecordArchiveTable (
	fk_record_id         varchar(255)     ,
	fk_archive_id        varchar(255)     ,
	FOREIGN KEY ( fk_archive_id ) REFERENCES ArchiveTable( archive_id ) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY ( fk_record_id ) REFERENCES RecordTable( record_id ) ON DELETE CASCADE ON UPDATE CASCADE
 );

CREATE TABLE TokenTable (
	token_id             varchar(255) NOT NULL    ,
	fk_user_id           bigint     ,
	token_expiration     datetime NOT NULL    ,
	FOREIGN KEY ( fk_user_id ) REFERENCES UserTable( user_id )
 );

CREATE INDEX Idx_token_expiration ON TokenTable ( token_expiration );
