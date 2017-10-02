/*
 * Database structure for testing
 *
 * In production these tables come from a remote database
 */

CREATE TYPE path_type AS ENUM ('file', 'directory', 'link');

CREATE TABLE metadata (
    md_hash UUID,
    md_ingested TIMESTAMP WITH TIME ZONE,
    md_type TEXT,
    md_json JSONB,
    PRIMARY KEY (md_hash, md_type)
);

CREATE TABLE paths (
    pa_hash UUID PRIMARY KEY,
    pa_ingested TIMESTAMP WITH TIME ZONE,
    pa_type PATH_TYPE,
    pa_path TEXT,
    pa_parents UUID[]
);

CREATE TABLE checksums (
    ch_hash UUID PRIMARY KEY,
    ch_md5 TEXT,
    ch_sha256 TEXT
);


-- Read sample data
/*
\copy (with x as (select * from esgf_filter limit 5) select y.* from metadata as y join x on md_hash = file_id) to db/metadata_sample.txt 
\copy (with x as (select * from esgf_filter limit 5) select y.* from checksums as y join x on ch_hash = file_id) to db/checksums_sample.txt 
\copy (with x as (select * from esgf_filter limit 5) select y.* from paths as y join x on pa_hash = file_id) to db/paths_sample.txt 
*/
\copy metadata  from 'db/metadata_sample.txt'
\copy paths     from 'db/paths_sample.txt'
\copy checksums from 'db/checksums_sample.txt'

