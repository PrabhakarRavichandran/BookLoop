-- ============================================================
-- BOOKLOOP - MySQL Database Schema
-- ============================================================

USE bookloop;

-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS wishlists;
DROP TABLE IF EXISTS offers;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS users;

-- ============================================================
-- USERS TABLE
-- ============================================================
CREATE TABLE users (
  id         BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,
  name       VARCHAR(120)     NOT NULL,
  dept       VARCHAR(50)      NOT NULL,
  year       VARCHAR(30)      NOT NULL,
  email      VARCHAR(180)     NOT NULL UNIQUE,
  password   VARCHAR(255)     NOT NULL,
  phone      VARCHAR(20)      DEFAULT '',
  avatar     VARCHAR(10)      DEFAULT '',
  created_at TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- BOOKS TABLE
-- ============================================================
CREATE TABLE books (
  id          BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,
  title       VARCHAR(255)     NOT NULL,
  author      VARCHAR(255)     NOT NULL,
  subject     VARCHAR(255)     NOT NULL,
  semester    VARCHAR(10)      NOT NULL,
  cond        VARCHAR(30)      NOT NULL,
  description TEXT,
  price       INT              NOT NULL DEFAULT 0,
  type        ENUM('Sell','Exchange','Donate') NOT NULL DEFAULT 'Sell',
  seller_id   BIGINT UNSIGNED  NOT NULL,
  seller_name VARCHAR(120)     NOT NULL,
  dept        VARCHAR(50)      NOT NULL,
  status      ENUM('AVAILABLE','RESERVED','SOLD') NOT NULL DEFAULT 'AVAILABLE',
  cover       VARCHAR(20)      DEFAULT '',
  color       VARCHAR(20)      DEFAULT '#6366F1',
  offer_count INT              NOT NULL DEFAULT 0,
  created_at  TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- OFFERS TABLE
-- ============================================================
CREATE TABLE offers (
  id               BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,
  book_id          BIGINT UNSIGNED  NOT NULL,
  book_title       VARCHAR(255)     NOT NULL,
  buyer_id         BIGINT UNSIGNED  NOT NULL,
  buyer_name       VARCHAR(120)     NOT NULL,
  buyer_dept       VARCHAR(50)      NOT NULL,
  offer_price      INT              NOT NULL DEFAULT 0,
  message          TEXT,
  status           ENUM('PENDING','ACCEPTED','REJECTED') NOT NULL DEFAULT 'PENDING',
  -- Safe Handover fields
  handover_code    VARCHAR(8)       DEFAULT NULL,
  tx_stage         ENUM('ACCEPTED','HANDOVER_PENDING','SELLER_CONFIRMED','COMPLETED') DEFAULT NULL,
  seller_confirmed TINYINT(1)       NOT NULL DEFAULT 0,
  buyer_confirmed  TINYINT(1)       NOT NULL DEFAULT 0,
  created_at       TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  FOREIGN KEY (book_id)  REFERENCES books(id)  ON DELETE CASCADE,
  FOREIGN KEY (buyer_id) REFERENCES users(id)  ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- WISHLISTS TABLE  (one row per user-book pair)
-- ============================================================
CREATE TABLE wishlists (
  id      BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id BIGINT UNSIGNED NOT NULL,
  book_id BIGINT UNSIGNED NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_wish (user_id, book_id),
  FOREIGN KEY (user_id) REFERENCES users(id)  ON DELETE CASCADE,
  FOREIGN KEY (book_id) REFERENCES books(id)  ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- WANTED BOOKS TABLE  (student requests for books they need)
-- ============================================================
CREATE TABLE wanted_books (
  id          BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,
  user_id     BIGINT UNSIGNED  NOT NULL,
  user_name   VARCHAR(120)     NOT NULL,
  user_dept   VARCHAR(50)      NOT NULL,
  title       VARCHAR(255)     NOT NULL,
  subject     VARCHAR(255)     NOT NULL DEFAULT '',
  semester    VARCHAR(10)      NOT NULL DEFAULT '',
  max_budget  INT              NOT NULL DEFAULT 0,
  message     TEXT,
  status      ENUM('OPEN','FULFILLED') NOT NULL DEFAULT 'OPEN',
  created_at  TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- SEED DATA
-- No pre-seeded users. All users must register via OTP verification.
-- Demo book data is created on-demand by the /api/demo/simulation endpoint.
-- ============================================================

