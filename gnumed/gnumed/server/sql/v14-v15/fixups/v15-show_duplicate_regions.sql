-- find duplicate regions
select
	id,
	code,
	name,
	country
from
	dem.state
where
	code || lower(name) || lower(country) in (
		select
			s.code || lower(s.name) || lower(s.country)
		from
			dem.state s
		group by
			s.code || lower(s.name) || lower(s.country)
		having
			count(*) > 1
	)
order by
	code,
	lower(name),
	lower(country)
;
