CREATE TABLE things ( 
    thing_id INT(5) AUTO_INCREMENT PRIMARY KEY, 
    UID CHAR(9) UNIQUE, 
    name VARCHAR(100) NOT NULL, 
    pwr_lvl INT(5) NOT NULL DEFAULT 1, 
    like_bal INT(10) NOT NULL DEFAULT 0, 
    wager_uid CHAR(9), 
    wager_likes INT(10) 
);
