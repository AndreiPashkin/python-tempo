DROP FUNCTION IF EXISTS tempo_timeintervalset_contains(
  timeintervalset tempo_timeintervalset,
  datetimes timestamp
);

DROP FUNCTION IF EXISTS tempo_timeintervalset_forward(
    timeintervalset tempo_timeintervalset, start timestamp, n integer
);

DROP DOMAIN IF EXISTS tempo_timeintervalset;
DROP FUNCTION IF EXISTS tempo_is_timeintervalset(jsonb);

DROP DOMAIN IF EXISTS tempo_timeinterval;
DROP FUNCTION IF EXISTS tempo_is_timeinterval(jsonb);

DROP DOMAIN IF EXISTS tempo_unit;
DROP FUNCTION IF EXISTS tempo_is_unit(jsonb);
