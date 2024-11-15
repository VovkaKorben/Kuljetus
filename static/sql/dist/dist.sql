SELECT
	d.*,cn1.city_name as city_name1,cn2.city_name as city_name2
FROM
	dist d
	INNER JOIN city_names cn1 ON d.city1 = cn1.city_id 
	AND cn1.city_name_lower = :city1
	INNER JOIN city_names cn2 ON d.city2 = cn2.city_id 
	AND cn2.city_name_lower = :city2
	LIMIT 1