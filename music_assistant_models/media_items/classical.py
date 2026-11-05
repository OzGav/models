"""Rows returned by the classical music listings."""

from __future__ import annotations

from dataclasses import dataclass, field

from mashumaro import DataClassDictMixin

from music_assistant_models.enums import ArtistRole, Period, WorkType

from .metadata import MediaItemImage
from .summary import ArtistSummary, WorkSummary


@dataclass(kw_only=True)
class ClassicalComposer(DataClassDictMixin):
    """A composer in the classical listings, with the size of their classical catalogue."""

    artist: ArtistSummary
    fanart: MediaItemImage | None = None  # the artist's fanart, as wide artwork for the row
    work_count: int = 0
    recording_count: int = 0
    country: str | None = None  # ISO 3166-1 code of the country they are from


@dataclass(kw_only=True)
class ClassicalPerformer(DataClassDictMixin):
    """A performer in the classical listings, with their performing roles."""

    artist: ArtistSummary
    fanart: MediaItemImage | None = None  # the artist's fanart, as wide artwork for the row
    main_role: ArtistRole  # the performing role with the most credits
    roles: list[ArtistRole] = field(default_factory=list)
    work_count: int = 0
    recording_count: int = 0


@dataclass(kw_only=True)
class ClassicalWorkEntry(DataClassDictMixin):
    """A work in the classical listings, with its number of recordings."""

    work: WorkSummary
    recording_count: int = 0
    part_names: list[str] = field(default_factory=list)  # names of its parts in the library
    period: Period | None = None  # the period of its (first) composer


@dataclass(kw_only=True)
class ClassicalComposerFilters(DataClassDictMixin):
    """The values the classical composers list can be filtered on, of all its composers."""

    periods: list[Period] = field(default_factory=list)
    countries: list[str] = field(default_factory=list)  # ISO 3166-1 codes
    country_unknown: bool = False  # whether any composer has no country


@dataclass(kw_only=True)
class ClassicalPerformerFilters(DataClassDictMixin):
    """The values the classical performers list can be filtered on, of all its performers."""

    roles: list[ArtistRole] = field(default_factory=list)


@dataclass(kw_only=True)
class ClassicalWorkFilters(DataClassDictMixin):
    """The values the classical works list can be filtered on, of all its works."""

    periods: list[Period] = field(default_factory=list)
    work_types: list[WorkType] = field(default_factory=list)
    work_type_unknown: bool = False  # whether any work has no type
    earliest_year: int | None = None  # the earliest year a work was composed
    latest_year: int | None = None  # the latest year a work was composed
