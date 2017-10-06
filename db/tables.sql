CREATE OR REPLACE VIEW esgf_filter AS
    SELECT
        pa_hash AS file_id
    FROM paths
    WHERE
        pa_type = 'file'
        AND (
            pa_parents[6] = md5('/g/data1/ua6/unofficial-ESG-replica/tmp/tree')::uuid
            OR  pa_parents[4] = md5('/g/data1/ua6/authoritative')::uuid
         );


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
    NATURAL JOIN esgf_filter;
CREATE INDEX IF NOT EXISTS esgf_metadata_dataset_link_file_id ON esgf_metadata_dataset_link(file_id);
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
        SELECT pa_hash, string_to_array(pa_path,'/') AS path_parts
        FROM paths JOIN esgf_filter ON pa_hash = file_id),
    y AS (
        SELECT pa_hash, path_parts[array_length(path_parts,1)-2] AS version
        FROM x),
    versions AS (
        SELECT pa_hash, SUBSTRING(version, '^v?(\d+)$') AS version  FROM y WHERE version ~* '^v?\d+$'),
    variables AS (
        SELECT pa_hash, split_part(path_parts[array_length(path_parts,1)],'_',1) AS variable
        FROM x),
    b AS (
        SELECT pa_hash, substring(pa_path,'\d+-\d+(?=\.nc$)') AS dates
        FROM paths JOIN esgf_filter ON pa_hash = file_id),
    c AS (
        SELECT pa_hash, substr(split_part(dates,'-',1),1,6)::int AS l, substr(split_part(dates,'-',2),1,6)::int AS h
        FROM b),
    d AS (
        SELECT pa_hash, int4range(l,h,'[]') AS period
        FROM c WHERE l <= h),
    access_versions AS (
        SELECT pa_hash, split_part(path_parts[array_length(path_parts,1)-1],'_',2) as access_version
        FROM x WHERE path_parts[5] = 'authoritative'
        )

    SELECT pa_hash as file_id, COALESCE(access_version, version) AS version, variable, period
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
