/* This is a binding of Python-Tempo library for using it with PostgreSQL. */


-- Checks if given jsonb string is a unit, used in Tempo.
CREATE OR REPLACE FUNCTION tempo_is_unit(item jsonb)
RETURNS boolean
IMMUTABLE
LANGUAGE plpgsql
AS $$
BEGIN
  IF item ISNULL
  THEN
    RETURN false;
  ELSE
    RETURN upper(item::text) IN ('"YEAR"', '"MONTH"', '"WEEK"',
                                 '"DAY"', '"HOUR"', '"MINUTE"', '"SECOND"');
  END IF;
END;
$$;


-- Time unit type.
CREATE DOMAIN tempo_unit AS jsonb
CONSTRAINT is_unit_check CHECK (
    tempo_is_unit(VALUE)
);


-- Checks if given jsonb is a valid time interval.
-- The format is [[1, 15], "month", "year"].
CREATE OR REPLACE FUNCTION tempo_is_recurrentevent(item jsonb)
RETURNS boolean
IMMUTABLE
LANGUAGE plpgsql
AS $$
DECLARE
  recurrence jsonb;
BEGIN
  IF item ISNULL
  THEN
    RETURN false;
  ELSE
    IF jsonb_typeof(item) != 'array' OR jsonb_array_length(item) != 4 THEN
      RETURN false;
    END IF;
    recurrence := item -> 3;
    RETURN (
      (WITH interval(value) AS (VALUES (item -> 0), (item -> 1))
       SELECT bool_and(value::text ~ '^\d+$')
       FROM interval) AND
      tempo_is_unit(item -> 2) AND
      (tempo_is_unit(recurrence) OR (recurrence = 'null'::jsonb))
    );
  END IF;
END;
$$;

-- Type for RecurrentEvent.
CREATE DOMAIN tempo_recurrentevent AS jsonb
CONSTRAINT is_recurrentevent_check CHECK (tempo_is_recurrentevent(VALUE));


  -- Checks if given jsonb is a valid recurrenteventset.
-- The format is ["AND", [[1, 15], "month", "year"]].
CREATE OR REPLACE FUNCTION tempo_is_recurrenteventset(item jsonb)
RETURNS boolean
IMMUTABLE
LANGUAGE plpgsql
AS $$
DECLARE
  e               jsonb;
  cur             jsonb;
  queued          jsonb[] := ARRAY[]::jsonb[];
  OPS    CONSTANT jsonb[] := ARRAY['"AND"', '"OR"', '"NOT"']::jsonb[];
BEGIN
  queued := array_append(queued, item);
  WHILE array_length(queued, 1) > 0 LOOP
    cur := queued [1];
    queued := queued [2:array_length(queued, 1)];
    IF (cur -> 0) = ANY (OPS) THEN
      cur := to_json((SELECT array_agg(elem) FROM
                        (SELECT jsonb_array_elements(cur) AS elem
                         OFFSET 1) AS _))::jsonb;
    ELSE
      RETURN false;
    END IF;
    FOR e IN SELECT jsonb_array_elements(cur) LOOP
      IF jsonb_typeof(e) = 'array' AND (e -> 0) = ANY (OPS) THEN
        queued := array_append(queued, e);
      ELSIF NOT (tempo_is_recurrentevent(e)) THEN
        RETURN false;
      END IF;
    END LOOP;
  END LOOP;
  RETURN true;
END
$$;

-- Type for recurrenteventset.
CREATE DOMAIN tempo_recurrenteventset AS jsonb
CONSTRAINT is_recurrenteventset_check CHECK (tempo_is_recurrenteventset(VALUE));


-- recurrenteventset containment test for a single datetime.
CREATE OR REPLACE FUNCTION
  tempo_recurrenteventset_contains(recurrenteventset tempo_recurrenteventset,
                                   datetime timestamp)
RETURNS boolean
IMMUTABLE
LANGUAGE plpythonu
AS $$
    from ciso8601 import parse_datetime
    from tempo.recurrenteventset import RecurrentEventSet

    return (parse_datetime(datetime) in
            RecurrentEventSet.from_json(recurrenteventset))
$$;


-- recurrenteventset forward intervals as set of rows.
CREATE OR REPLACE FUNCTION
  tempo_recurrenteventset_forward(recurrenteventset tempo_recurrenteventset,
                                  start timestamp,
                                  n integer,
                                  clamp bool DEFAULT true)
RETURNS TABLE(start timestamp, stop timestamp)
IMMUTABLE
LANGUAGE plpythonu
AS $$
    import itertools as it
    from ciso8601 import parse_datetime
    from tempo.recurrenteventset import RecurrentEventSet

    for interval in it.islice(RecurrentEventSet
                                  .from_json(recurrenteventset)
                                  .forward(start=parse_datetime(start),
                                           trim=clamp),
                              n):
        yield interval
$$;
