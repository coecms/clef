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
            realm ||'.'||
            'r'||r||'i'||i||'p'||p
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
        model,
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
    
/* Extra metadata not stored in the file itself
 */
CREATE TABLE IF NOT EXISTS extended_metadata (
    file_id UUID PRIMARY KEY,
    version TEXT,
    variable TEXT,
    period INT4RANGE  /* Date stored as a 8 character integer, e.g. 19800101
                         to avoid calendar issues */
    );
GRANT SELECT ON extended_metadata TO PUBLIC;

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

