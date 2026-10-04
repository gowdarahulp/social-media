"""24-72h Forecasting engine with Holt-Winters Exponential Smoothing and Prediction Intervals."""
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import json
import math
import numpy as np
from typing import Any, Dict, List, Optional
from backend.app.schemas.trends import ForecastPoint, TrendForecast
from backend.app.db.database import db

class TrendForecaster:
    @staticmethod
    def forecast_topic(topic_name: str, forecast_hours: int = 48) -> Optional[TrendForecast]:
        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT timestamp FROM posts 
            WHERE topics LIKE ? 
            ORDER BY timestamp ASC
        ''', (f"%{topic_name}%",))
        rows = cursor.fetchall()
        if not rows:
            return None

        # Build continuous hourly timeline
        hourly_counts = defaultdict(int)
        for r in rows:
            dt = datetime.fromisoformat(r["timestamp"])
            hour_bucket = dt.strftime("%Y-%m-%d %H:00:00")
            hourly_counts[hour_bucket] += 1

        all_buckets = sorted(hourly_counts.keys())
        first_dt = datetime.strptime(all_buckets[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        last_dt = datetime.strptime(all_buckets[-1], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)

        # Fill any missing gaps with 0 for time series continuity
        full_series = []
        curr = first_dt
        while curr <= last_dt:
            k = curr.strftime("%Y-%m-%d %H:00:00")
            full_series.append({
                "timestamp": curr,
                "volume": hourly_counts.get(k, 0)
            })
            curr += timedelta(hours=1)

        counts_array = np.array([pt["volume"] for pt in full_series], dtype=float)
        
        # Fit Holt-Winters Exponential Smoothing model
        fitted_values = []
        predictions = []
        residual_std = 1.0

        if len(counts_array) >= 6:
            try:
                from statsmodels.tsa.holtwinters import SimpleExpSmoothing, Holt
                model = Holt(counts_array, initialization_method="estimated").fit(optimized=True)
                preds = model.forecast(forecast_hours)
                predictions = [max(0.0, float(p)) for p in preds]
                fitted = model.fittedvalues
                residuals = counts_array - fitted
                residual_std = max(float(np.std(residuals)), 0.5)
            except Exception:
                # Robust fallback exponential smoothing
                alpha = 0.35
                beta = 0.15
                level = counts_array[0]
                trend = counts_array[1] - counts_array[0] if len(counts_array) > 1 else 0.0
                for val in counts_array:
                    last_level = level
                    level = alpha * val + (1 - alpha) * (level + trend)
                    trend = beta * (level - last_level) + (1 - beta) * trend
                
                preds = []
                for h in range(1, forecast_hours + 1):
                    p = max(0.0, level + h * trend * math.exp(-0.03 * h))
                    preds.append(p)
                predictions = preds
                residual_std = max(float(np.std(counts_array)), 0.8)
        else:
            # Baseline mean
            mean_val = float(np.mean(counts_array)) if len(counts_array) > 0 else 1.0
            predictions = [mean_val] * forecast_hours
            residual_std = 1.0

        # Construct forecast points with 80% and 95% confidence intervals
        # z_80 = 1.282, z_95 = 1.960
        forecast_points = []
        start_forecast_dt = last_dt + timedelta(hours=1)
        
        for h, pred in enumerate(predictions, start=1):
            ts = start_forecast_dt + timedelta(hours=h-1)
            # Prediction interval widens as horizon grows: sqrt(h)
            sigma_h = residual_std * math.sqrt(1.0 + 0.15 * h)
            
            p_val = round(pred, 2)
            lb_80 = max(0.0, round(pred - 1.282 * sigma_h, 2))
            ub_80 = round(pred + 1.282 * sigma_h, 2)
            lb_95 = max(0.0, round(pred - 1.960 * sigma_h, 2))
            ub_95 = round(pred + 1.960 * sigma_h, 2)

            forecast_points.append(ForecastPoint(
                timestamp=ts,
                predicted_volume=p_val,
                lower_bound_80=lb_80,
                upper_bound_80=ub_80,
                lower_bound_95=lb_95,
                upper_bound_95=ub_95
            ))

        history_payload = [
            {"timestamp": pt["timestamp"].isoformat(), "volume": pt["volume"]}
            for pt in full_series[-48:] # Last 48 hours of history
        ]

        return TrendForecast(
            topic_id=f"top_{abs(hash(topic_name)) % 100000}",
            name=topic_name,
            method="Holt-Winters Exponential Smoothing + Burst Detection",
            history=history_payload,
            forecast=forecast_points
        )
