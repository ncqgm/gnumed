-- find duplicate streets
select
	id, name,
	postcode
from
	dem.street
where
	id_urb || lower(name) || lower(postcode) in (
		select
			s.id_urb || lower(name) || lower(postcode)
		from
			dem.street s
		group by
			s.id_urb || lower(s.name) || lower(s.postcode)
		having
			count(*) > 1
	)
order by
	id_urb,
	lower(name),
	lower (postcode)
;
