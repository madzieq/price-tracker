import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


class MLService:
    def predict_price(
        self, price_history: list[dict], days_ahead: int = 7
    ) -> dict:
        if len(price_history) < 5:
            return {"prediction": None, "confidence": 0, "message": "Za mało danych"}

        df = pd.DataFrame(price_history)
        df["scraped_at"] = pd.to_datetime(df["scraped_at"])
        df = df.sort_values("scraped_at")
        df["day_index"] = (df["scraped_at"] - df["scraped_at"].min()).dt.days

        X = df["day_index"].values.reshape(-1, 1)
        y = df["price"].values

        model = LinearRegression()
        model.fit(X, y)

        last_day = df["day_index"].max()
        future_day = np.array([[last_day + days_ahead]])
        predicted_price = float(model.predict(future_day)[0])

        score = model.score(X, y)
        confidence = round(max(0, min(score * 100, 99)), 1)

        trend = "down" if model.coef_[0] < 0 else "up"

        return {
            "predicted_price": round(predicted_price, 2),
            "confidence": confidence,
            "trend": trend,
            "days_ahead": days_ahead,
        }

    def get_statistics(self, prices: list[float]) -> dict:
        if not prices:
            return {}
        arr = np.array(prices)
        return {
            "min": round(float(arr.min()), 2),
            "max": round(float(arr.max()), 2),
            "mean": round(float(arr.mean()), 2),
            "std": round(float(arr.std()), 2),
            "current": round(float(arr[-1]), 2),
        }
