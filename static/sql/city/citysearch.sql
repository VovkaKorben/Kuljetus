SELECT
	cl.city_id, 
    cl.city_name, 
    cl.region_name
FROM
(
SELECT 
    cn.city_id, 
    cn.city_name, 
    MIN(cn.lang) AS lang, 
    r.region_name
FROM 
    city_names cn
	LEFT JOIN cities c ON c.city_id = cn.city_id 
	LEFT JOIN regions r ON r.region_id = c.city_region 	AND r.lang = cn.lang 
WHERE 
    cn.city_name_lower LIKE :cityname || '%' 
GROUP BY 
    cn.city_id
ORDER BY 
	c.population DESC
	limit 6
) cl
ORDER BY cl.city_name asc;