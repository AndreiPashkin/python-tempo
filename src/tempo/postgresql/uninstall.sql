DROP FUNCTION IF EXISTS tempo_recurrenteventset_contains(
  recurrenteventset tempo_recurrenteventset,
  datetimes timestamp
);

DROP FUNCTION IF EXISTS tempo_recurrenteventset_forward(
    recurrenteventset tempo_recurrenteventset, start timestamp, n integer,
    clamp bool DEFAULT true
);

DROP DOMAIN IF EXISTS tempo_recurrenteventset;
DROP FUNCTION IF EXISTS tempo_is_recurrenteventset(jsonb);

DROP DOMAIN IF EXISTS tempo_recurrentevent;
DROP FUNCTION IF EXISTS tempo_is_recurrentevent(jsonb);

DROP DOMAIN IF EXISTS tempo_unit;
DROP FUNCTION IF EXISTS tempo_is_unit(jsonb);
