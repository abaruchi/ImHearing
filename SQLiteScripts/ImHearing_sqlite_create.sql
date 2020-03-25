CREATE TABLE RecordTable (
	record_id            varchar(255) NOT NULL  PRIMARY KEY  ,
	record_date          date     ,
	record_start         datetime     ,
	record_end           datetime     ,
	record_size          bigint     ,
	uploaded             boolean     ,
	path                 varchar(255)
 );

CREATE INDEX Idx_record_start ON RecordTable ( record_start );

CREATE INDEX Idx_record_date ON RecordTable ( record_date );

CREATE TABLE UserTable (
	user_id              bigint NOT NULL  PRIMARY KEY  ,
	user_name            varchar(100) NOT NULL    ,
	user_email           varchar(100)     ,
	user_pass            varchar(100) NOT NULL    ,
	user_lastlogin       datetime     ,
	CONSTRAINT Idx_user_id UNIQUE ( user_id )
 );

CREATE TABLE ScheduleRecordsTable (
	schedule_id          bigint NOT NULL  PRIMARY KEY  ,
	fk_user_id           bigint     ,
	fk_record_id         varchar(255)     ,
	schedule_start       datetime     ,
	schedule_end         datetime     ,
	FOREIGN KEY ( fk_user_id ) REFERENCES UserTable( user_id )  ,
	FOREIGN KEY ( fk_record_id ) REFERENCES RecordTable( record_id )
 );

CREATE INDEX Idx_schedule_start ON ScheduleRecordsTable ( schedule_start );

CREATE TABLE TokenTable (
	token_id             varchar(255) NOT NULL  PRIMARY KEY  ,
	fk_user_id           bigint     ,
	token_expiration     datetime NOT NULL    ,
	FOREIGN KEY ( fk_user_id ) REFERENCES UserTable( user_id )
 );

CREATE INDEX Idx_token_expiration ON TokenTable ( token_expiration );
