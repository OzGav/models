"""Tests for classical-music model additions: Credit, Work, Recording and related fields."""

from music_assistant_models.enums import ArtistRole, ExternalID, MediaType, Period, WorkType
from music_assistant_models.media_items import (
    Album,
    Artist,
    Credit,
    ItemMapping,
    ItemMappingSummary,
    Recording,
    Track,
    Work,
    WorkSummary,
    media_from_dict,
)
from music_assistant_models.unique_list import UniqueList


def _artist_mapping(name: str, item_id: str = "1") -> ItemMapping:
    """Build a minimal artist ItemMapping for tests."""
    return ItemMapping(
        item_id=item_id,
        provider="test",
        name=name,
        media_type=MediaType.ARTIST,
    )


def test_work_construction_and_mbid_roundtrip() -> None:
    """Work supports MusicBrainz Work MBID via external_ids and the mbid property."""
    work = Work(
        item_id="w1",
        provider="test",
        name="Symphony No. 5 in C minor, Op. 67",
        provider_mappings=set(),
        catalog_numbers=["Op. 67"],
        work_type=WorkType.SYMPHONY,
    )
    work.mbid = "f47ac10b-58cc-4372-a567-0e02b2c3d479"
    assert work.mbid == "f47ac10b-58cc-4372-a567-0e02b2c3d479"
    assert (ExternalID.MB_WORK, "f47ac10b-58cc-4372-a567-0e02b2c3d479") in work.external_ids


def test_work_roundtrips_via_media_from_dict() -> None:
    """media_from_dict dispatches MediaType.WORK to Work.from_dict correctly."""
    work = Work(
        item_id="w1",
        provider="test",
        name="Brandenburg Concerto No. 5",
        provider_mappings=set(),
        work_type=WorkType.CONCERTO,
    )
    restored = media_from_dict(work.to_dict())
    assert isinstance(restored, Work)
    assert restored.name == "Brandenburg Concerto No. 5"
    assert restored.work_type == WorkType.CONCERTO


def test_track_credit_convenience_properties() -> None:
    """Track.composers / conductors / performers_with_instruments filter by role."""
    composer = _artist_mapping("Beethoven", "a1")
    conductor = _artist_mapping("Karajan", "a2")
    soloist = _artist_mapping("Heifetz", "a3")
    performer = _artist_mapping("Section Violinist", "a4")

    track = Track(
        item_id="t1",
        provider="test",
        name="Symphony No. 5: I. Allegro con brio",
        provider_mappings=set(),
        credits=[
            Credit(artist=composer, role=ArtistRole.COMPOSER, position=0),
            Credit(artist=conductor, role=ArtistRole.CONDUCTOR, position=0),
            Credit(artist=soloist, role=ArtistRole.SOLOIST, instrument="violin", position=0),
            Credit(artist=performer, role=ArtistRole.PERFORMER, instrument=None, position=1),
        ],
    )

    assert track.composers == [composer]
    assert track.conductors == [conductor]
    assert track.performers_with_instruments == [(soloist, "violin"), (performer, None)]


def test_track_credits_returned_in_position_order() -> None:
    """Credits added out of position order are returned sorted by position within their role."""
    a1 = _artist_mapping("Composer1", "a1")
    a2 = _artist_mapping("Composer2", "a2")
    a3 = _artist_mapping("Composer3", "a3")

    track = Track(
        item_id="t1",
        provider="test",
        name="Some Work",
        provider_mappings=set(),
        credits=[
            Credit(artist=a3, role=ArtistRole.COMPOSER, position=2),
            Credit(artist=a1, role=ArtistRole.COMPOSER, position=0),
            Credit(artist=a2, role=ArtistRole.COMPOSER, position=1),
        ],
    )
    assert track.composers == [a1, a2, a3]


def test_track_classical_fields_default_to_none() -> None:
    """Work / movement_* / credits default sensibly for non-classical tracks."""
    track = Track(
        item_id="t1",
        provider="test",
        name="Pop song",
        provider_mappings=set(),
    )
    assert track.work is None
    assert track.movement_number is None
    assert track.movement_total is None
    assert track.movement_name is None
    assert track.credits == []


def test_album_credit_convenience_properties() -> None:
    """Album.composers / conductors filter credits by role."""
    composer = _artist_mapping("Beethoven", "a1")
    conductor = _artist_mapping("Karajan", "a2")
    album = Album(
        item_id="al1",
        provider="test",
        name="Karajan conducts Beethoven",
        provider_mappings=set(),
        credits=[
            Credit(artist=composer, role=ArtistRole.COMPOSER),
            Credit(artist=conductor, role=ArtistRole.CONDUCTOR),
        ],
    )
    assert album.composers == [composer]
    assert album.conductors == [conductor]


def test_artistrole_unknown_falls_back_to_performer() -> None:
    """ArtistRole._missing_ returns PERFORMER for forward compatibility."""
    assert ArtistRole("not_a_real_role") == ArtistRole.PERFORMER


def test_worktype_unknown_falls_back_to_other() -> None:
    """WorkType._missing_ returns OTHER for forward compatibility."""
    assert WorkType("not_a_real_type") == WorkType.OTHER


def test_artistrole_serializes_to_string_value() -> None:
    """ArtistRole serializes to its plain string value and deserializes back."""
    credit = Credit(artist=_artist_mapping("Karajan"), role=ArtistRole.CONDUCTOR)
    payload = credit.to_dict()
    assert payload["role"] == "conductor"
    assert Credit.from_dict(payload).role is ArtistRole.CONDUCTOR


def test_credit_roundtrip() -> None:
    """Credit survives to_dict/from_dict, including instrument and position."""
    credit = Credit(
        artist=_artist_mapping("Heifetz"),
        role=ArtistRole.SOLOIST,
        instrument="violin",
        position=2,
    )
    restored = Credit.from_dict(credit.to_dict())
    assert isinstance(restored.artist, ItemMapping)
    assert restored.to_dict() == credit.to_dict()


def test_work_full_roundtrip() -> None:
    """Work round-trips losslessly with composers, MusicBrainz Work ID and all its fields."""
    work = Work(
        item_id="w1",
        provider="test",
        name="Requiem in D minor, K. 626",
        provider_mappings=set(),
        composers=UniqueList([_artist_mapping("Mozart", "a1"), _artist_mapping("Süssmayr", "a2")]),
        catalog_numbers=["K. 626"],
        work_type=WorkType.MASS,
        parent_work=ItemMapping(
            item_id="w0", provider="test", name="Parent", media_type=MediaType.WORK
        ),
        composition_year=1791,
        language="Latin",
        musical_key="D minor",
    )
    work.add_external_id(ExternalID.MB_WORK, "f47ac10b-58cc-4372-a567-0e02b2c3d479")
    payload = work.to_dict()
    restored = Work.from_dict(payload)
    assert [x.name for x in restored.composers] == ["Mozart", "Süssmayr"]
    assert restored.mbid == "f47ac10b-58cc-4372-a567-0e02b2c3d479"
    assert restored.composition_year == 1791
    assert restored.language == "Latin"
    assert restored.musical_key == "D minor"
    assert restored.to_dict() == payload


def test_track_and_album_defaults_serialize_cleanly() -> None:
    """Non-classical tracks and albums serialize the new fields as empty defaults."""
    track = Track(item_id="t1", provider="test", name="Pop song", provider_mappings=set())
    track_payload = track.to_dict()
    assert track_payload["credits"] == []
    assert track_payload["work"] is None
    assert track_payload["movement_number"] is None
    assert track_payload["is_classical"] is False
    assert Track.from_dict(track_payload).to_dict() == track_payload

    album = Album(item_id="al1", provider="test", name="Pop album", provider_mappings=set())
    album_payload = album.to_dict()
    assert album_payload["credits"] == []
    assert album_payload["is_classical"] is False
    assert Album.from_dict(album_payload).to_dict() == album_payload


def test_track_and_album_credits_roundtrip() -> None:
    """Populated credits and movement fields on tracks and albums round-trip losslessly."""
    classical_credits = [
        Credit(artist=_artist_mapping("Beethoven", "a1"), role=ArtistRole.COMPOSER),
        Credit(artist=_artist_mapping("Karajan", "a2"), role=ArtistRole.CONDUCTOR),
        Credit(artist=_artist_mapping("Berliner Philharmoniker", "a3"), role=ArtistRole.ORCHESTRA),
    ]
    track = Track(
        item_id="t1",
        provider="test",
        name="Symphony No. 5: I. Allegro con brio",
        provider_mappings=set(),
        credits=classical_credits,
        work=ItemMapping(
            item_id="w1", provider="test", name="Symphony No. 5", media_type=MediaType.WORK
        ),
        movement_number=1,
        movement_total=4,
        movement_name="I. Allegro con brio",
        is_classical=True,
    )
    track_payload = track.to_dict()
    restored_track = Track.from_dict(track_payload)
    assert restored_track.conductors[0].name == "Karajan"
    assert restored_track.work is not None
    assert restored_track.work.media_type == MediaType.WORK
    assert restored_track.to_dict() == track_payload

    album = Album(
        item_id="al1",
        provider="test",
        name="Beethoven: Symphony No. 5",
        provider_mappings=set(),
        credits=classical_credits,
        is_classical=True,
    )
    album_payload = album.to_dict()
    assert Album.from_dict(album_payload).to_dict() == album_payload


def test_artist_classical_fields_roundtrip() -> None:
    """Artist.period and is_classical round-trip."""
    artist = Artist(
        item_id="a1",
        provider="test",
        name="Bach",
        provider_mappings=set(),
        period=Period.BAROQUE,
        is_classical=True,
    )
    payload = artist.to_dict()
    assert payload["period"] == "baroque"
    restored = Artist.from_dict(payload)
    assert restored.period is Period.BAROQUE
    assert restored.is_classical is True


def test_artist_unknown_period_deserializes_to_none() -> None:
    """A period value unknown to this version deserializes to None instead of failing."""
    payload = Artist(item_id="a1", provider="test", name="X", provider_mappings=set()).to_dict()
    payload["period"] = "not_a_real_period"
    assert Artist.from_dict(payload).period is None


def test_work_summary_roundtrip() -> None:
    """WorkSummary round-trips and omits None-valued keys, also in nested composers."""
    summary = WorkSummary(
        item_id="w1",
        provider="library",
        name="Symphony No. 5",
        composers=UniqueList(
            [
                ItemMappingSummary(
                    item_id="a1", provider="library", name="Beethoven", media_type=MediaType.ARTIST
                )
            ]
        ),
        catalog_numbers=["Op. 67"],
        work_type=WorkType.SYMPHONY,
        composition_year=1808,
    )
    payload = summary.to_dict()
    assert payload["media_type"] == "work"
    assert not [k for k, v in payload.items() if v is None]
    assert not [k for k, v in payload["composers"][0].items() if v is None]
    restored = WorkSummary.from_dict(payload)
    assert restored.to_dict() == payload
    assert isinstance(media_from_dict(payload), Work)


def test_recording_roundtrip() -> None:
    """Recording round-trips with its movement tracks, credits and album."""
    tracks = [
        Track(
            item_id=f"t{number}",
            provider="test",
            name=f"Movement {number}",
            provider_mappings=set(),
            duration=600,
            movement_number=number,
        )
        for number in (1, 2)
    ]
    recording = Recording(
        key="w1:karajan:1963",
        work=ItemMapping(
            item_id="w1", provider="test", name="Symphony No. 5", media_type=MediaType.WORK
        ),
        tracks=tracks,
        credits=[Credit(artist=_artist_mapping("Karajan"), role=ArtistRole.CONDUCTOR)],
        year=1963,
        album=ItemMapping(item_id="al1", provider="test", name="Album", media_type=MediaType.ALBUM),
        duration=1200,
    )
    payload = recording.to_dict()
    restored = Recording.from_dict(payload)
    assert [x.movement_number for x in restored.tracks] == [1, 2]
    assert restored.credits[0].role is ArtistRole.CONDUCTOR
    assert restored.to_dict() == payload
