create or replace function clin.is_unique_narrative() returns trigger as '
BEGIN
        perform  * from clin.clin_narrative c where c.soap_cat = NEW.soap_cat and c.fk_encounter = NEW.fk_encounter and md5(c.narrative) = NEW.narrative ;
        if found then
                       raise exception ''Cannot update duplicate narrative in same encounter.'';
 		       return OLD;
        end if;
        return NEW;
	END;
' language 'plpgsql';

drop trigger  tr_narrative_no_duplicate  on clin.clin_narrative;
create trigger tr_narrative_no_duplicate after update or insert on clin.clin_narrative for each row
					execute procedure clin.is_unique_narrative();

