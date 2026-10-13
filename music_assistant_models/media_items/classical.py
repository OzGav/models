"""Rows returned by the classical music listings."""

from __future__ import annotations

from dataclasses import dataclass, field

from mashumaro import DataClassDictMixin

from music_assistant_models.enums import ArtistRole, Period

from .metadata import MediaItemImage
from .summary import ArtistSummary, WorkSummary


@dataclass(kw_only=True)
class ClassicalComposer(DataClassDictMixin):
    """A composer in the classical listings, with the size of their classical catalogue."""

    artist: ArtistSummary
    fanart: MediaItemImage | None = None  # the artist's fanart, as wide artwork for the row
    work_count: int = 0
    recording_count: int = 0


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
