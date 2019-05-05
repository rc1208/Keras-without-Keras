drop table if exists training_data;

create table training_data (
    id TEXT PRIMARY KEY,
    type TEXT, 
    description TEXT,
    date_created TEXT,
    file_number INTERGER,
    if_ignore_1stline TEXT,
    if_target_category TEXT 
);

create index type_index on training_data(type);

/*insert into training_data (id, type, description, date_created, file_number, if_ignore_1stline, if_target_category)
values ("example", "tabular", "example data", "2019-04-20 15:00:00", 1, "on", "on") */

