DROP FUNCTION IF EXISTS tempo_timeintervalset_contains(
  timeintervalset tempo_timeintervalset,
  datetimes timestamptz
);
DROP FUNCTION IF EXISTS tempo_timeintervalset_contains(
  timeintervalset tempo_timeintervalset,
  datetimes timestamptz[2]
);

DROP DOMAIN IF EXISTS tempo_timeintervalset;
DROP FUNCTION IF EXISTS tempo_is_timeintervalset(jsonb);

DROP DOMAIN IF EXISTS tempo_timeinterval;
DROP FUNCTION IF EXISTS tempo_is_timeinterval(jsonb);

DROP DOMAIN IF EXISTS tempo_unit;
DROP FUNCTION IF EXISTS tempo_is_unit(jsonb);
