# quantcode/trading/ - Trade Log

`trade_log.json` is the persistent record of every paper trade the bot makes,
started 2026-09-08 after an honest self-assessment: with only a handful of
trades, no conclusion about real performance is possible, and the biggest gap
was having no structured record to eventually compute real statistics from.

## Rules for future updates

- On every new trade (after the user confirms via `suggest_trade`/
  `suggest_trades_batch`): append an entry with `signals_at_entry` describing
  the actual reasoning used (catalyst / technical / positioning - whichever
  applied), not a generic placeholder.
- On every close (TP hit, SL hit, or manual close): update that trade's
  `status`, `exit_price`, `exit_date`, `result_pct`, `outcome_notes`. Check
  `get_portfolio` against this file's `status: "open"` entries during each
  scheduled check to catch closes that happened between checks.
- Do not compute `stats` (win_rate, avg_r_multiple, expectancy) until there
  are enough *closed* trades for it to be meaningful (rough rule of thumb:
  20+). Before that, leave `stats` as `null` and say so honestly in any
  content or status report - a stat computed on 3-5 closed trades is noise,
  not signal.
- Never backfill `signals_at_entry` for old trades with reasoning that wasn't
  actually used at the time - mark it "not recorded at entry time" instead,
  as done for the initial Day 1 batch.
