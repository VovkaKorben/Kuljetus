SELECT
	DISTINCT cn.city_id,	cn.city_name
	
FROM
	city_names cn
	
WHERE
	cn.city_name_lower = :cityname;