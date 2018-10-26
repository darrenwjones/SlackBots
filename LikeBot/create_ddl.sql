CREATE TABLE users (
  UID CHAR(9) PRIMARY KEY, 
  first_name VARCHAR(25) NOT NULL, 
  last_name VARCHAR(25) NOT NULL, 
  pwr_lvl INT(5) NOT NULL DEFAULT 1, 
  like_bal INT(10) NOT NULL DEFAULT 0, 
  wager_uid CHAR(9), 
  wager_likes INT(10), 
  CONSTRAINT user_wager_fk FOREIGN KEY(wager_uid) REFERENCES users(UID)
);
