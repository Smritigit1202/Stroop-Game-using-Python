import sqlite3

def show_efficiency_data():
    print("\n[DEBUG] Fetching data from database...\n")
    conn = sqlite3.connect('stroop_efficiency.db')
    c = conn.cursor()

    try:
        c.execute("SELECT * FROM efficiency")
        rows = c.fetchall()

        if not rows:
            print("[INFO] No data found in 'efficiency' table.")
        else:
            print(f"{'Method':<15} {'Language':<10} {'Highest Eff.':<15} {'Average Eff.':<15} {'Games Played'}")
            print("-" * 70)
            for row in rows:
                method, language, high_eff, avg_eff, games = row
                print(f"{method:<15} {language:<10} {high_eff:<15.2f} {avg_eff:<15.2f} {games}")
    except Exception as e:
        print(f"[ERROR] Failed to read database: {e}")
    finally:
        conn.close()
        print("\n[DEBUG] Done.\n")

# Run it
show_efficiency_data()
