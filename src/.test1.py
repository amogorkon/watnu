selected_space = 1

s = f"""
SELECT id FROM tasks
WHERE
done == FALSE AND
deleted == FALSE AND
draft == FALSE AND
inactive == FALSE
{f"AND space_id == {selected_space}" if selected_space else ""}
"""
print(s)