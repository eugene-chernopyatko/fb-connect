import sqlite3

conn = sqlite3.connect('/home/neyokee/fb-connect/db.sqlite3')
cursor = conn.cursor()

user_id = cursor.execute('SELECT id FROM authentication_customuser')
user_id_list = user_id.fetchall()

for ids in user_id_list:
    projects_count = cursor.execute(f'SELECT id FROM datatransfer_project WHERE user_id = {ids[0]}')
    projects_count_list = projects_count.fetchall()
    cursor.execute(f'UPDATE authentication_customuser SET '
                   f'project_count = "{len(projects_count_list)}"'
                   f'WHERE id={ids[0]}')
    conn.commit()