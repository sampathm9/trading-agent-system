from datetime import datetime
from database.database import get_connection

class DecisionRepository:

    def save(self, decision):
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                action TEXT NOT NULL,
                confidence REAL,
                reason TEXT,
                strategy_pnl REAL,
                strategy_win_rate REAL
            )
            '''
        )

        cursor.execute(
            '''
            INSERT INTO decisions (
                created_at,
                action,
                confidence,
                reason,
                strategy_pnl,
                strategy_win_rate
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (
                datetime.now().isoformat(),
                decision.get('action'),
                decision.get('confidence'),
                decision.get('reason'),
                decision.get('strategy_pnl'),
                decision.get('strategy_win_rate')
            )
        )

        connection.commit()
        connection.close()
