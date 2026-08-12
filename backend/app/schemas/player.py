from datetime import datetime

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
)

import re

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

DOMAIN_PATTERN = re.compile(
    r"^(?:[a-z0-9-]+\.)+[a-z]{2,}(?:/.*)?$",
    re.IGNORECASE,
)


class GameResultCreate(BaseModel):
    game_id: str

    player_id: str

    player_name: str = Field(
        min_length=2,
        max_length=100,
    )

    company_name: str = Field(
        min_length=2,
        max_length=150,
    )

    score: int = Field(
        ge=0,
    )

    lightning_collected: int = Field(
        ge=0,
    )

    duration: float = Field(
        gt=0,
    )

    @field_validator(
        "company_name",
    )
    @classmethod
    def validate_company_name(
        cls,
        value: str,
    ) -> str:
        company = value.strip()

        if EMAIL_PATTERN.match(company):
            raise ValueError("Company name cannot be an email address.")

        if DOMAIN_PATTERN.match(company):
            raise ValueError("Company name cannot be a website.")

        return company


    @field_validator("player_name")
    @classmethod
    def validate_player_name(
        cls,
        value: str,
    ) -> str:
        name = value.strip()

        if EMAIL_PATTERN.fullmatch(name):
            raise ValueError("Player name cannot be an email address.")

        if DOMAIN_PATTERN.fullmatch(name):
            raise ValueError("Player name cannot be a website.")

        # Must contain at least one letter
        if not any(char.isalpha() for char in name):
            raise ValueError("Enter a valid player name.")

        # Only allow letters and normal name punctuation
        if not all(char.isalpha() or char in " '-'." for char in name):
            raise ValueError("Enter a valid player name.")

        return name


class GameResultResponse(BaseModel):
    game_id: str

    player_id: str

    player_name: str

    company_name: str

    score: int

    lightning_collected: int

    duration: float

    created_at: datetime


class LeaderboardRow(BaseModel):
    rank: int

    player_name: str

    company_name: str

    score: int

    lightning_collected: int


class LeaderboardEntryCreate(BaseModel):
    game_id: str

    player_id: str

    email: EmailStr

    # marketing_consent: bool = False


class LeaderboardEntryResponse(BaseModel):
    success: bool

    game_id: str

    player_id: str

    score: int

    rank: int
