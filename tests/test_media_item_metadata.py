"""Tests for MediaItemMetadata."""

from music_assistant_models.media_items.metadata import MediaItemMetadata


def test_last_musicbrainz_lookup_defaults_to_none() -> None:
    """A metadata blob written before the field existed reads back as never looked up."""
    assert MediaItemMetadata.from_dict({}).last_musicbrainz_lookup is None


def test_update_always_overwrites_last_musicbrainz_lookup() -> None:
    """A newer lookup timestamp replaces the stored one, like last_refresh does."""
    metadata = MediaItemMetadata(last_musicbrainz_lookup=100)
    metadata.update(MediaItemMetadata(last_musicbrainz_lookup=200))
    assert metadata.last_musicbrainz_lookup == 200


def test_update_always_overwrites_last_musicbrainz_recording_lookup() -> None:
    """A newer recording lookup timestamp replaces the stored one, like the other markers."""
    metadata = MediaItemMetadata(last_musicbrainz_recording_lookup=100)
    metadata.update(MediaItemMetadata(last_musicbrainz_recording_lookup=200))
    assert metadata.last_musicbrainz_recording_lookup == 200


def test_update_keeps_a_stored_recording_year() -> None:
    """An update fills an empty recording year and keeps a stored one."""
    metadata = MediaItemMetadata()
    metadata.update(MediaItemMetadata(recording_year=1962))
    metadata.update(MediaItemMetadata(recording_year=1977))
    assert metadata.recording_year == 1962
    assert MediaItemMetadata.from_dict({"recording_year": 1986}).recording_year == 1986
