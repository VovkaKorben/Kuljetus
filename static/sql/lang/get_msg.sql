SELECT
	* 
FROM
	selector_translation st 
WHERE
	st.language_id = :language_id 
	AND st.selector_id = :selector_id;