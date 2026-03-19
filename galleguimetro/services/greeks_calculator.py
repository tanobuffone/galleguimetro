import logging
from typing import Dict, Any
from datetime import datetime, date

import QuantLib as ql

from ..models.schemas import OptionData, Greeks, GreeksRequest, GreeksResponse

logger = logging.getLogger(__name__)


class GreeksCalculator:
    """Servicio de cálculo de griegas usando QuantLib."""

    def __init__(self):
        ql.Settings.instance().evaluationDate = ql.Date().todaysDate()
        logger.info("QuantLib GreeksCalculator inicializado.")

    def _setup_option_environment(
        self,
        option_data: OptionData,
        spot_price: float,
        risk_free_rate: float,
        dividend_yield: float,
        time_to_expiration_years: float,
    ) -> tuple:
        """Configura el entorno de QuantLib para la opción."""
        today = ql.Date().todaysDate()
        maturity_date = ql.Date(
            option_data.expiration_date.day,
            option_data.expiration_date.month,
            option_data.expiration_date.year,
        )
        ql.Settings.instance().evaluationDate = today

        volatility = option_data.implied_volatility if option_data.implied_volatility is not None else 0.20

        day_count = ql.Actual365Fixed()
        r = ql.FlatForward(today, ql.QuoteHandle(ql.SimpleQuote(risk_free_rate)), day_count)
        q = ql.FlatForward(today, ql.QuoteHandle(ql.SimpleQuote(dividend_yield)), day_count)
        sigma = ql.BlackConstantVol(today, ql.NullCalendar(), volatility, day_count)

        bsm_process = ql.BlackScholesMertonProcess(
            ql.QuoteHandle(ql.SimpleQuote(spot_price)),
            ql.YieldTermStructureHandle(q),
            ql.YieldTermStructureHandle(r),
            ql.BlackVolTermStructureHandle(sigma),
        )

        engine = ql.AnalyticEuropeanEngine(bsm_process)

        option_type_ql = ql.Option.Call if option_data.option_type.value.upper() == "CALL" else ql.Option.Put
        payoff = ql.PlainVanillaPayoff(option_type_ql, option_data.strike_price)
        exercise = ql.EuropeanExercise(maturity_date)
        option_ql = ql.VanillaOption(payoff, exercise)
        option_ql.setPricingEngine(engine)

        return option_ql, bsm_process, engine

    def calculate_greeks(self, request: GreeksRequest) -> GreeksResponse:
        """Calcula las griegas para una opción dada."""
        option_data = request.option_data
        spot_price = request.spot_price
        risk_free_rate = request.risk_free_rate
        dividend_yield = request.dividend_yield
        time_to_expiration_years = request.time_to_expiration_years

        expiration_ql_date = ql.Date(
            option_data.expiration_date.day,
            option_data.expiration_date.month,
            option_data.expiration_date.year,
        )

        if time_to_expiration_years is None or time_to_expiration_years <= 0:
            evaluation_date_ql = ql.Date().todaysDate()
            if evaluation_date_ql > expiration_ql_date:
                raise ValueError("La fecha de evaluación no puede ser posterior a la de vencimiento.")
            day_count = ql.Actual365Fixed()
            time_to_expiration_years = day_count.yearFraction(evaluation_date_ql, expiration_ql_date)

        if time_to_expiration_years <= 1e-6:
            raise ValueError("El tiempo hasta el vencimiento es demasiado corto o cero.")

        option_ql, bsm_process, engine = self._setup_option_environment(
            option_data, spot_price, risk_free_rate, dividend_yield, time_to_expiration_years
        )

        greeks_calc = Greeks()
        try:
            greeks_calc.delta = float(option_ql.delta())
            greeks_calc.gamma = float(option_ql.gamma())
            greeks_calc.theta = float(option_ql.theta())
            greeks_calc.vega = float(option_ql.vega())
            greeks_calc.rho = float(option_ql.rho())
        except Exception as e:
            logger.error(f"Error al calcular griegas con QuantLib: {e}")
            raise RuntimeError(f"Error en cálculo de griegas: {e}")

        input_parameters = {
            "option_symbol": option_data.symbol,
            "spot_price": spot_price,
            "strike_price": option_data.strike_price,
            "time_to_expiration_years": time_to_expiration_years,
            "risk_free_rate": risk_free_rate,
            "dividend_yield": dividend_yield,
            "implied_volatility": option_data.implied_volatility,
            "option_type": option_data.option_type.value,
            "expiration_date": option_data.expiration_date.isoformat(),
        }

        return GreeksResponse(
            option_symbol=option_data.symbol,
            greeks=greeks_calc,
            input_parameters=input_parameters,
            calculation_timestamp=datetime.utcnow(),
        )

    def get_market_data_from_dde(self) -> Dict[str, Any]:
        """Placeholder para DDE - se implementará con win32com en Windows."""
        logger.debug("DDE: función placeholder, retornando vacío.")
        return {}

    def calculate_portfolio_greeks(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder para griegas agregadas de portfolio."""
        logger.debug("Portfolio greeks: placeholder.")
        return {"portfolio_delta": 0.0, "portfolio_gamma": 0.0, "portfolio_vega": 0.0, "portfolio_theta": 0.0}
