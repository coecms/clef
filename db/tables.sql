CREATE OR REPLACE VIEW metadata AS
    SELECT
        md_hash,
        md_type,
        md_json
    FROM rr3.metadata
    UNION ALL
    SELECT
        md_hash,
        md_type,
        md_json
    FROM ua6.metadata;

CREATE OR REPLACE VIEW paths AS
    SELECT
        pa_hash,
        pa_type,
        pa_path,
        pa_parents
    FROM rr3.paths
    UNION ALL
    SELECT
        pa_hash,
        pa_type,
        pa_path,
        pa_parents
    FROM ua6.paths;

CREATE OR REPLACE VIEW esgf_filter AS
    SELECT
        pa_hash AS file_id
    FROM paths
    WHERE
        pa_type IN ('file', 'link')
        AND (
            pa_parents[6] = md5('/g/data1/ua6/unofficial-ESG-replica/tmp/tree')::uuid
            OR pa_parents[4] = md5('/g/data1/rr3/publications')::uuid
         );

CREATE MATERIALIZED VIEW IF NOT EXISTS esgf_paths AS
    SELECT
        file_id,
        pa_path AS path
    FROM esgf_filter
    JOIN paths ON file_id = pa_hash;
CREATE UNIQUE INDEX IF NOT EXISTS esgf_path_file_id_idx ON esgf_paths(file_id);

CREATE MATERIALIZED VIEW IF NOT EXISTS checksums AS
    SELECT
        md_hash as ch_hash,
        md_json->>'md5' as ch_md5,
        md_json->>'sha256' as ch_sha256
    FROM metadata
    JOIN esgf_paths ON md_hash = file_id
    WHERE md_type = 'checksum';
CREATE UNIQUE INDEX IF NOT EXISTS checksums_hash_idx ON checksums(ch_hash);
CREATE INDEX IF NOT EXISTS checksums_md5_idx ON checksums(ch_md5);
CREATE INDEX IF NOT EXISTS checksums_sha256_idx ON checksums(ch_sha256);

CREATE OR REPLACE VIEW dataset_metadata AS
    SELECT
        md_hash AS file_id,
        md_json->'attributes'->>'project_id' as project,
        md_json->'attributes'->>'product' as product,
        md_json->'attributes'->>'institute_id' as institute,
        md_json->'attributes'->>'model_id' as model,
        md_json->'attributes'->>'experiment_id' as experiment,
        md_json->'attributes'->>'frequency' as frequency,
        md_json->'attributes'->>'modeling_realm' as realm,
        md_json->'attributes'->>'realization' as r,
        md_json->'attributes'->>'initialization_method' as i,
        md_json->'attributes'->>'physics_version' as p
    FROM metadata
    WHERE md_type = 'netcdf';


CREATE MATERIALIZED VIEW IF NOT EXISTS esgf_metadata_dataset_link AS
    SELECT
        file_id,
        md5(
            COALESCE(project,'') ||'.'||
            COALESCE(product,'') ||'.'||
            COALESCE(institute,'') ||'.'||
            model ||'.'||
            experiment ||'.'||
            frequency ||'.'||
            COALESCE(realm,'') ||'.'||
            COALESCE('r'||r||'i'||i||'p'||p,'')
        )::uuid as dataset_id
    FROM dataset_metadata
    NATURAL JOIN esgf_paths;
CREATE UNIQUE INDEX IF NOT EXISTS esgf_metadata_dataset_link_file_id ON esgf_metadata_dataset_link(file_id);
CREATE INDEX IF NOT EXISTS esgf_metadata_dataset_link_dataset_id ON esgf_metadata_dataset_link(dataset_id);
GRANT SELECT ON esgf_metadata_dataset_link TO PUBLIC;


CREATE MATERIALIZED VIEW IF NOT EXISTS esgf_dataset AS
    SELECT DISTINCT
        dataset_id,
        project,
        product,
        institute,
        CASE WHEN model = 'ACCESS1-0' THEN 'ACCESS1.0'
            WHEN model = 'ACCESS1-3' THEN 'ACCESS1.3'
            WHEN model = 'CSIRO-Mk3-6-0' THEN 'CSIRO-Mk3.6.0'
            ELSE model END
            AS model,
        experiment,
        frequency,
        realm,
        r,
        i,
        p,
        'r'||r||'i'||i||'p'||p AS ensemble
    FROM dataset_metadata
    NATURAL JOIN esgf_metadata_dataset_link;
CREATE INDEX IF NOT EXISTS esgf_dataset_dataset_id ON esgf_dataset(dataset_id);
GRANT SELECT ON esgf_dataset TO PUBLIC;
    
/* Extra metadata not stored in the file itself. This table stores manually
 * entered data, automatic data is in the view `extended_metadata_path` and
 * both are combined in the materialized view `extended_metadata`.
 *
 * Users should go through the 'extended_metadata' table
 */
CREATE TABLE IF NOT EXISTS extended_metadata_manual (
    file_id UUID PRIMARY KEY,
    version TEXT,
    variable TEXT,
    period INT4RANGE  /* Date stored as a 6 character integer, e.g. 198001
                         to avoid calendar issues */
    );

/* Users can add their own messages here
 */
CREATE TABLE IF NOT EXISTS errata (
    id SERIAL PRIMARY KEY,
    value TEXT,
    added_by TEXT DEFAULT CURRENT_USER,
    added_on TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
GRANT SELECT ON errata TO PUBLIC;
GRANT INSERT (value) ON errata TO PUBLIC;

/* Links an errata message to a file
 */
CREATE TABLE IF NOT EXISTS file_errata_link (
    errata_id INTEGER REFERENCES errata(id) ON DELETE CASCADE,
    file_id UUID,
    added_by TEXT DEFAULT CURRENT_USER,
    added_on TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (errata_id, file_id)
    );
GRANT SELECT ON file_errata_link TO PUBLIC;
GRANT INSERT (errata_id, file_id) ON file_errata_link TO PUBLIC;

/* Gather information from the file path that isn't present in the file
 * attributes. This won't always be correct, values can be overriden by adding
 * a row in `extended_metadata_manual` and refreshing `extended_metadata`
 */
CREATE OR REPLACE VIEW extended_metadata_path AS
    WITH x AS (
        SELECT file_id, string_to_array(path,'/') AS path_parts
        FROM esgf_paths),
    y AS (
        SELECT file_id, path_parts[array_length(path_parts,1)-2] AS version
        FROM x),
    versions AS (
        SELECT file_id, SUBSTRING(version, '^v?(\d+)$') AS version  FROM y WHERE version ~* '^v?\d+$'),
    variables AS (
        SELECT file_id, split_part(path_parts[array_length(path_parts,1)],'_',1) AS variable
        FROM x),
    b AS (
        SELECT file_id, substring(path,'\d+-\d+(?=\.nc$)') AS dates
        FROM esgf_paths),
    c AS (
        SELECT file_id, substr(split_part(dates,'-',1),1,6)::int AS l, substr(split_part(dates,'-',2),1,6)::int AS h
        FROM b),
    d AS (
        SELECT file_id, int4range(l,h,'[]') AS period
        FROM c WHERE l <= h),
    access_versions AS (
        SELECT file_id, split_part(path_parts[array_length(path_parts,1)-1],'_',2) as access_version
        FROM x WHERE path_parts[5] = 'authoritative'
        )

    SELECT file_id, COALESCE(access_version, version) AS version, variable, period
    FROM variables
    NATURAL LEFT JOIN versions
    NATURAL LEFT JOIN access_versions
    NATURAL LEFT JOIN d;

CREATE MATERIALIZED VIEW IF NOT EXISTS extended_metadata AS
    SELECT
        file_id, 
        COALESCE(m.version, p.version) AS version,
        COALESCE(m.variable, p.variable) AS variable,
        COALESCE(m.period, p.period) AS period
    FROM extended_metadata_path AS p
    NATURAL LEFT JOIN extended_metadata_manual AS m;
GRANT SELECT ON extended_metadata TO PUBLIC;
