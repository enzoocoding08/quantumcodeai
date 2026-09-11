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

## Watchlist scope (updated 2026-09-11, on user's explicit request)

After 4 consecutive Day-1-long stop-losses (all correlated to one macro
risk-off wave, not independent bad calls - see the closed entries above),
the user asked to screen a *broader* set of assets per check so more real
setups get a chance to surface, while explicitly keeping the 3-signal bar
(catalyst + technical confirmation + positioning) as high as before -
"handle wie ein Wall Street super trader, geh richtig gut bedachte trades
ein" (well-considered trades, not more trades for their own sake).

Concretely: each scheduled check should screen a wider basket than just the
original watchlist.json tickers - include more of the daily story-analysis
universe (all 28 tickers, not just the ones currently held), more crypto
majors/alts beyond BTC/ETH/SOL/XRP, indices (SP500, XYZ100), and metals
(GOLD, SILVER) each time, not just when something already looks interesting.
More assets screened != more trades taken. A trade is proposed only when
the same 3-signal confluence bar is met - broadening the search widens the
net, it does not lower the bar. Do not increase leverage as a way to
"catch up" on losses - leverage scales losses exactly as much as gains and
does not address the actual problem (correlated position sizing on
same-direction batches). If the user explicitly asks to loosen the
confluence threshold itself (e.g. accept 2/3 signals with a documented
reason), tag those trades distinctly in `signals_at_entry` so they don't
get silently mixed into the same stats as full-confluence trades later.
