SELECT
	sl.selector_name,
	sl.attr,
	st.translation 
FROM
	selector_translation st
	LEFT JOIN selector_list sl ON sl.selector_id = st.selector_id 
WHERE
	st.language_id = :lang
	and
	sl.selector_id>=0;