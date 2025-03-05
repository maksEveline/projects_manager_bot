import sqlite3


def update_end_date():
    conn = sqlite3.connect("data/database.db")
    cur = conn.cursor()
    cur.execute("SELECT sub_id, user_id, project_id, rate_id FROM active_subscriptions")
    rows = cur.fetchall()
    for sub_id, user_id, project_id, rate_id in rows:
        cur.execute(
            "UPDATE active_subscriptions SET purchase_type=? WHERE sub_id=?",
            ("undefined", sub_id),
        )

    conn.commit()
    conn.close()


update_end_date()
