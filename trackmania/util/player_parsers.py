"""
MIT License

Copyright (c) 2022-present Deepesh Nimma

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import division

from typing import Dict, List

from trackmania.structures.player import PlayerSearchResult

from ..structures.player import (
    PlayerMatchmaking,
    PlayerMetaInfo,
    PlayerTrophies,
    PlayerZone,
)

__all__ = ("PlayerParsers",)

# pylint: disable=too-few-public-methods, too-many-locals
class PlayerParsers:
    """Internal Method to parse data required for PlayerManager functions."""

    @staticmethod
    def parse_data(data: Dict) -> tuple:
        """
        Parses the JSON data into the required data types for the Player constructor.

        :param data: The JSON data to parse.
        :type data: Dict
        :return: the parsed data as a tuple.
        :rtype: tuple
        """

        display_name = data["displayname"]
        player_id = data["accountid"]
        first_login = data["timestamp"]

        try:
            club_tag = data["clubtag"]
            club_tag_timestamp = data["clubtagtimestamp"]
        except KeyError:
            club_tag, club_tag_timestamp = None, None
        trophy_points = data["trophies"]["points"]
        trophy_count = data["trophies"]["counts"]
        last_trophy = data["trophies"]["timestamp"]
        echelon = data["trophies"]["echelon"]

        zones = data["trophies"]["zone"]
        zone_positions = data["trophies"]["zonepositions"]

        try:
            player_meta = PlayerParsers._parse_meta(data["meta"])
        except KeyError:
            player_meta = None

        player_trophies = PlayerTrophies(
            echelon, last_trophy, trophy_points, trophy_count, player_id
        )
        player_zones = PlayerParsers._parse_zones(zones, zone_positions)

        player_mm_data = PlayerParsers._parse_matchmaking(data["matchmaking"])
        threes, royal = player_mm_data[0], player_mm_data[1]

        return (
            club_tag,
            first_login,
            player_id,
            club_tag_timestamp,
            display_name,
            player_meta,
            display_name,
            player_trophies,
            player_zones,
            threes,
            royal,
        )

    @staticmethod
    def _parse_zones(zones: Dict, zone_positions: List[int]) -> List[PlayerZone]:
        """
        Parses the Data from the API into a list of PlayerZone objects.

        :param zones: the zones data from the API.
        :type zones: Dict
        :param zone_positions: The zone positions data from the API.
        :type zone_positions: List[int]
        :return: The list of PlayerZone objects.
        :rtype: List[PlayerZone]
        """
        if len(zone_positions) == 3:
            player_zone_list = []

            player_zone_list.append(
                PlayerZone(zones["flag"], zones["name"], zone_positions[0])
            )
            player_zone_list.append(
                PlayerZone(
                    zones["parent"]["flag"], zones["parent"]["name"], zone_positions[1]
                )
            )
            player_zone_list.append(
                PlayerZone(
                    zones["parent"]["parent"]["flag"],
                    zones["parent"]["parent"]["name"],
                    zone_positions[2],
                )
            )
        elif len(zone_positions) == 4:
            player_zone_list = []

            player_zone_list.append(
                PlayerZone(zones["flag"], zones["name"], zone_positions[0])
            )
            player_zone_list.append(
                PlayerZone(
                    zones["parent"]["flag"], zones["parent"]["name"], zone_positions[1]
                )
            )
            player_zone_list.append(
                PlayerZone(
                    zones["parent"]["parent"]["flag"],
                    zones["parent"]["parent"]["name"],
                    zone_positions[2],
                )
            )
            player_zone_list.append(
                PlayerZone(
                    zones["parent"]["parent"]["parent"]["flag"],
                    zones["parent"]["parent"]["parent"]["name"],
                    zone_positions[3],
                )
            )
        elif len(player_zone_list) == 5:
            player_zone_list = []

            player_zone_list.append(
                PlayerZone(zones["flag"], zones["name"], zone_positions[0])
            )
            player_zone_list.append(
                PlayerZone(
                    zones["parent"]["flag"], zones["parent"]["name"], zone_positions[1]
                )
            )
            player_zone_list.append(
                PlayerZone(
                    zones["parent"]["parent"]["flag"],
                    zones["parent"]["parent"]["name"],
                    zone_positions[2],
                )
            )
            player_zone_list.append(
                PlayerZone(
                    zones["parent"]["parent"]["parent"]["flag"],
                    zones["parent"]["parent"]["parent"]["name"],
                    zone_positions[3],
                )
            )
            player_zone_list.append(
                PlayerZone(
                    zones["parent"]["parent"]["parent"]["parent"]["flag"],
                    zones["parent"]["parent"]["parent"]["parent"]["name"],
                    zone_positions[4],
                )
            )
        else:
            player_zone_list = None

        return player_zone_list

    @staticmethod
    def _parse_meta(metadata: Dict) -> PlayerMetaInfo:
        """
        Parses the Meta Data from the API into a PlayerMetaInfo object.

        :param metadata: The metadata data from the API.
        :type metadata: Dict
        :return: The parsed data
        :rtype: PlayerMetaInfo
        """
        # Please someone teach me a better way of doing this...
        try:
            twitter = metadata["twitter"]
        except KeyError:
            twitter = None

        try:
            twitch = metadata["twitch"]
        except KeyError:
            twitch = None

        try:
            youtube = metadata["youtube"]
        except KeyError:
            youtube = None

        try:
            vanity = metadata["vanity"]
        except KeyError:
            vanity = None

        try:
            sponsor = metadata["sponsor"]
            sponsor_level = metadata["sponsorlevel"]
        except KeyError:
            sponsor = False
            sponsor_level = 0

        try:
            nadeo = metadata["nadeo"]
        except KeyError:
            nadeo = False

        try:
            tmgl = metadata["tmgl"]
        except KeyError:
            tmgl = False

        try:
            tmwc21 = metadata["tmwc21"]
        except KeyError:
            tmwc21 = False

        try:
            team = metadata["team"]
        except KeyError:
            team = False

        return PlayerMetaInfo(
            vanity,
            nadeo,
            tmgl,
            team,
            tmwc21,
            sponsor,
            sponsor_level,
            twitch,
            twitter,
            youtube,
            vanity,
        )

    @staticmethod
    def _parse_matchmaking(data: List[Dict]) -> List[PlayerMatchmaking]:
        """
		Parses the Matchmaking data of the player and returns 2 PlayerMatchmaking objects.\
			One for 3v3 Matchmaking and One for Royal Matchmaking.

		:param data: The matchmaking data.
		:type data: List[Dict]
		:return: The list of matchmaking data, one for 3v3 and the other for royal.
		:rtype: List[PlayerMatchmaking]
		"""
        matchmaking_data = []

        try:
            matchmaking_data.append(PlayerParsers.__parse_3v3(data[0]))
        except KeyError:
            matchmaking_data.append(None)

        try:
            matchmaking_data.append(PlayerParsers.__parse_3v3(data[1]))
        except KeyError:
            matchmaking_data.append(None)

        return matchmaking_data

    @staticmethod
    def __parse_3v3(data: Dict) -> PlayerMatchmaking:
        """
        Parses matchmaking data for 3v3 and royal type matchmaking.

        :param data: The matchmaking data only.
        :type data: Dict
        :return: The parsed data.
        :rtype: PlayerMatchmaking
        """
        typename = data["info"]["typename"]
        typeid = data["info"]["typeid"]
        rank = data["info"]["rank"]
        score = data["info"]["score"]
        progression = data["info"]["progression"]
        division = data["info"]["division"]["position"]
        min_points = data["info"]["division"]["minpoints"]
        max_points = data["info"]["division"]["maxpoints"]

        return PlayerMatchmaking(
            typename, typeid, progression, rank, score, division, min_points, max_points
        )

    @staticmethod
    def _parse_search_results(data: Dict) -> PlayerSearchResult:
        """
        Parses the search result of a single player.

        :param data: Player data.
        :type data: Dict
        :return: Parsed data in a PlayerSearchResult object.
        :rtype: PlayerSearchResult
        """
        name = data["player"]["name"]
        player_id = data["player"]["id"]

        try:
            club_tag = data["player"]["tag"]
        except KeyError:
            club_tag = None

        zone_data = PlayerParsers._parse_zones(
            data["player"]["zone"], [-1, -1, -1, -1, -1]
        )

        matchmaking_data = PlayerParsers._parse_matchmaking(
            data["player"]["matchmaking"]
        )

        return (
            club_tag,
            name,
            player_id,
            zone_data,
            matchmaking_data[0],
            matchmaking_data[1],
        )
