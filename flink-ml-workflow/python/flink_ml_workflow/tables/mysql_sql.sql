create table history_proto(
name varchar (100) unique,
typeId int default 0,
instanceId int AUTO_INCREMENT primary key,
properties varchar (100),
type varchar (100),
referId int,
referName varchar (100),
startTime bigint,
endTime bigint,
uri varchar (100)
);

create table example_proto(
name varchar (100) unique,
typeId int default 0,
instanceId int AUTO_INCREMENT primary key,
properties varchar (100),
supportType varchar (100),
nameList varchar (100),
typeList varchar (100),
exampleFormat varchar (100),
batchUri varchar (100),
streamUri varchar (100),
runMod varchar (100)
);

create table model_proto(
name varchar (100) unique,
typeId int default 0,
instanceId int AUTO_INCREMENT primary key,
properties varchar (100),
modelType varchar (100),
uri varchar (100)
);

create table model_version_proto(
name varchar (100) default null ,
typeId int default 0,
instanceId int AUTO_INCREMENT primary key,
properties varchar (100),
modelId int,
modelUri varchar (100),
logUri varchar (100),
version varchar (100) unique,
foreign key (modelId)
references model_proto(instanceId)
);

create table project_proto(
instanceId int AUTO_INCREMENT primary key,
name varchar (100) unique ,
typeId int default 0,
properties varchar (100) ,
projectType varchar (100),
uri varchar (100),
user varchar (100),
password varchar (100)
);