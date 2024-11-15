SELECT
	sl.selector_name,
	sl.attr,
	st.translation 
FROM
	selector_translation st
	LEFT JOIN selector_list sl ON sl.selector_id = st.selector_id 
WHERE
	st.language_id = :language_id 
AND 
	st.selector_id = :selector_id;