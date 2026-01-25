-- Create and select database
CREATE DATABASE IF NOT EXISTS twitter;
USE twitter;

-- Clean slate (safe to re-run)
DROP TABLE IF EXISTS TWEET;
DROP TABLE IF EXISTS FOLLOWS;

-- Tweets table
CREATE TABLE TWEET (
    tweet_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    tweet_ts DATETIME NOT NULL,
    tweet_text VARCHAR(140) NOT NULL,
    INDEX idx_user_ts (user_id, tweet_ts),
    INDEX idx_ts (tweet_ts)
);

-- Follows table
CREATE TABLE FOLLOWS (
    follower_id INT NOT NULL,
    followee_id INT NOT NULL,
    INDEX idx_follower (follower_id),
    INDEX idx_followee (followee_id),
    UNIQUE KEY uq_follow (follower_id, followee_id)
);

SELECT COUNT(*) FROM FOLLOWS;