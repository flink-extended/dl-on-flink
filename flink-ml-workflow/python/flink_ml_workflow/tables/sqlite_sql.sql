sqlite3 /Users/yiwen/sourcecode/tywFlink/flink-ai-extended/flink-ml-workflow/python/flink_ml_workflow/store/meta_data.db

create table model_proto(
instanceId integer primary key autoincrement not null ,
name text unique,
typeId int default 0,
properties text,
modelType text,
uri text
);

create table model_version_proto(
instanceId integer primary key autoincrement not null ,
name text default null,
typeId int default 0,
properties text,
modelId int,
modelUri text,
logUri text,
version text unique,
foreign key (modelId)
references model_proto(instanceId)
);

insert into model_proto(name, properties, modelType, uri)
values ('name1','{"a":"b"}','H5','www.google.com');

insert into model_proto( name, properties, modelType, uri)
values ('name2','{"a":"b"}','H5','www.taobao.com');

insert into model_version_proto(properties, modelId, modelUri, logUri, version)
values ('{"c":"d"}',1,'a','b','version_name1');

insert into model_version_proto(properties, modelId, modelUri, logUri, version)
values ('{"e":"f"}',2,'a','b','version_name2');

create table example_proto(
instanceId integer primary key autoincrement not null ,
name text unique ,
typeId int default 0,
properties text ,
supportType text,
nameList text,
typeList text,
exampleFormat text,
batchUri text,
streamUri text,
runMod text default null
);


insert into example_proto(name, supportType, nameList, typeList, exampleFormat, batchUri, streamUri,properties)
values ('example1','EXAMPLE_STREAM','["a","b"]','["Int32","Int32"]','a','b','c','{}');

create table history_proto(
instanceId integer primary key autoincrement not null ,
name text unique ,
typeId int default 0,
properties text ,
type text,
referId int ,
referName text,
startTime int,
endTime int,
uri text,
foreign key (referId) references project_proto(instanceId),
foreign key (referName) references project_proto(name)
);


create table project_proto(
instanceId integer primary key autoincrement not null ,
name text unique ,
typeId int default 0,
properties text ,
projectType text,
uri text,
user text,
password text
);

insert into project_proto(name, properties, projectType, uri, "user", password)
values ('pro1','{}','str','a','yiwen','yuanyuan');





