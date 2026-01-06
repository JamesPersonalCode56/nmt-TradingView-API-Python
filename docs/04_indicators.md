# 04 - Indicators

## PineIndicator

Fetch public indicators via `getIndicator`:

```python
import tradingview_api as TradingView

indicator = TradingView.getIndicator("STD;Supertrend%Strategy")
indicator.setOption("commission_type", "percent")
```

Attach to a chart:

```python
study = chart.Study(indicator)
study.onUpdate(lambda changes=None: print(study.periods[:1]))
```

Useful properties:

- `indicator.description`
- `indicator.shortDescription`
- `indicator.inputs`
- `indicator.plots`

## BuiltInIndicator

```python
volume = TradingView.BuiltInIndicator("VbPFixed@tv-basicstudies-241!")
volume.setOption("first_bar_time", int(time.time() * 1000) - 10**8)
study = chart.Study(volume)
```

Built-in indicators may require auth depending on type.

## Strategy report

For strategy scripts, the study updates `study.strategyReport`:

- `strategyReport.trades`
- `strategyReport.performance`
- `strategyReport.history`

## Graphics

Some indicators emit graphics (labels, lines, tables, etc).
Access them via:

```python
study.graphic
```

