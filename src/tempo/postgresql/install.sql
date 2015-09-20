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
CREATE OR REPLACE FUNCTION tempo_is_timeinterval(item jsonb)
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
    IF jsonb_typeof(item) != 'array' THEN
      RETURN false;
    recurrence := item -> 2;
    END IF;
    RETURN (
      jsonb_array_length(item -> 0) = 2 AND
      (SELECT bool_and(e ~ '^\d+$')
       FROM jsonb_array_elements_text(item -> 0) AS e) AND
      tempo_is_unit(item -> 1) AND
      (tempo_is_unit(recurrence) OR (recurrence = 'null'::jsonb))
    );
  END IF;
END;
$$;

-- Type for TimeInterval.
CREATE DOMAIN tempo_timeinterval AS jsonb
CONSTRAINT is_timeinterval_check CHECK (tempo_is_timeinterval(VALUE));


-- Checks if given jsonb is a valid timeintervalset.
-- The format is ["AND", [[1, 15], "month", "year"]].
CREATE OR REPLACE FUNCTION tempo_is_timeintervalset(item jsonb)
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
      ELSIF NOT (tempo_is_timeinterval(e)) THEN
        RETURN false;
      END IF;
    END LOOP;
  END LOOP;
  RETURN true;
END
$$;

-- Type for TimeIntervalSet.
CREATE DOMAIN tempo_timeintervalset AS jsonb
CONSTRAINT is_timeintervalset_check CHECK (tempo_is_timeintervalset(VALUE));


-- TimeIntervalSet containment test for a single datetime.
CREATE OR REPLACE FUNCTION
  tempo_timeintervalset_contains(timeintervalset tempo_timeintervalset,
                                 datetime timestamp)
RETURNS boolean
IMMUTABLE
LANGUAGE plpythonu
AS $$
    from ciso8601 import parse_datetime
    from tempo.timeintervalset import TimeIntervalSet

    return (parse_datetime(datetime) in
            TimeIntervalSet.from_json(timeintervalset))
$$;
