drop database if exists blog;
create database blog;
use blog;

create table Roles(
id int primary key;
name varchar(255);
permissions int not null;
);

create table User(
id int primary key;
role int not null;
email varchar(256) not null;
name varchar(256) not null;
birthDate timestamp not null;
creationDate timestamp not null;
);
