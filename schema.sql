drop table if exists keys;
create table keys (
  id integer primary key autoincrement,
  type text not null,
  -- trust
  length text not null,
  algo text not null, -- 1=RSA 16=Elgamal 17=DSA 20=Elgamal(sign/encrypt)
  keyid text not null,
  cdate text not null,
  expire text
  -- serial number
  -- ownertrust
  -- userid text
  -- sig class
  -- key capabilities
  -- FPR records
  -- edit flag
  -- sec/sbb serial
);
drop table if exists userids;
create table userids (
  id integer primary key autoincrement,
  keyid text not null,
  userid text not null
);
