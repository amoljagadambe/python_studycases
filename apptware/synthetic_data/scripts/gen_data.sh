#!/bin/bash

dbuser="root"
dbpassword="root"
dbname="pieces_common"

function generate_fake_data() {
    # $1->module_name, $2->param
    python /app/commands/fake_data_generator.py --module_name $1 --parameter $2 --folder "/tmp"
}

function load_data_in_sql() {
    # TODO: handle module_name parameter
    echo "Module name: $1"
    declare -a tablenames=("Organization" "STG_PIECES_physiciannote" "physiciannote_properties" "provider_type")
    for table_name in "${tablenames[@]}"; do
        query="LOAD DATA LOCAL INFILE '/tmp/$table_name.csv' INTO TABLE $table_name FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;"
        echo $query | mysql --user=$dbuser --password=$dbpassword $dbname
        echo "Data loaded in MySQL for table: $table_name"
    done
}

echo "Generating fake data"
generate_fake_data $1 $2
echo "Generated fake data"

if [ "$1" == "note_preprocessor" ]; then
    echo "Loading data in MySQL"
    load_data_in_sql $1
    echo "Successfully loaded in MySQL"
fi
