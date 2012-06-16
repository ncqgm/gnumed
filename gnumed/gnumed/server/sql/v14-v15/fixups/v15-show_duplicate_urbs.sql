-- find duplicate urbs (cities, towns, etc)
select
	id,
	name,
	postcode
from
	dem.urb
where
	id_state || lower(name) || lower(postcode) in (
		select
			u.id_state || lower(u.name) || lower(u.postcode)
		from
			dem.urb u
		group by
			u.id_state || lower(u.name) || lower(u.postcode)
		having
			count(*) > 1
	)
order by
	id_state,
	lower(name),
	lower(postcode)
;
