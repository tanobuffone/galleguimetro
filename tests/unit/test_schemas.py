import pytest
from datetime import date, timedelta
from galleguimetro.models.schemas import (
    OptionData, OptionType, Greeks, GreeksRequest,
    PortfolioCreate, PortfolioUpdate, PositionCreate,
    UserCreate, UserLogin, PaginationParams,
)


class TestOptionData:
    def test_valid_option_data(self):
        future_date = date.today() + timedelta(days=30)
        option = OptionData(
            symbol="AAPL240315C00200000",
            underlying_symbol="AAPL",
            option_type=OptionType.CALL,
            strike_price=200.0,
            expiration_date=future_date,
        )
        assert option.symbol == "AAPL240315C00200000"
        assert option.option_type == OptionType.CALL

    def test_expired_option_raises_error(self):
        past_date = date.today() - timedelta(days=1)
        with pytest.raises(ValueError, match="futuro"):
            OptionData(
                symbol="AAPL",
                underlying_symbol="AAPL",
                option_type=OptionType.CALL,
                strike_price=200.0,
                expiration_date=past_date,
            )

    def test_negative_strike_raises_error(self):
        with pytest.raises(ValueError):
            OptionData(
                symbol="AAPL",
                underlying_symbol="AAPL",
                option_type=OptionType.PUT,
                strike_price=-10.0,
                expiration_date=date.today() + timedelta(days=30),
            )


class TestGreeks:
    def test_greeks_defaults_to_none(self):
        g = Greeks()
        assert g.delta is None
        assert g.gamma is None

    def test_greeks_with_values(self):
        g = Greeks(delta=0.55, gamma=0.03, theta=-0.05, vega=0.15, rho=0.02)
        assert g.delta == 0.55
        assert g.vega == 0.15


class TestCRUDSchemas:
    def test_portfolio_create(self):
        p = PortfolioCreate(name="Mi Portfolio")
        assert p.name == "Mi Portfolio"
        assert p.description is None

    def test_portfolio_create_empty_name_fails(self):
        with pytest.raises(ValueError):
            PortfolioCreate(name="")

    def test_user_create_short_password_fails(self):
        with pytest.raises(ValueError):
            UserCreate(username="user", email="a@b.com", password="short")

    def test_user_login(self):
        login = UserLogin(username="testuser", password="testpass123")
        assert login.username == "testuser"

    def test_pagination_defaults(self):
        p = PaginationParams()
        assert p.page == 1
        assert p.page_size == 10
