# -*- coding: utf-8 -*-
from mahjong.constants import AKA_DORA_LIST
from mahjong.tile import TilesConverter
from mahjong.utils import simplify, is_honor, plus_dora


class DiscardOption(object):
    player = None

    # in 34 tile format
    tile_to_discard = None
    # array of tiles that will improve our hand
    waiting = None
    # how much tiles will improve our hand
    tiles_count = None
    # calculated tile value, for sorting
    value = None

    def __init__(self, player, tile_to_discard, waiting, tiles_count):
        """
        :param player:
        :param tile_to_discard: tile in 34 format
        :param waiting: list of tiles in 34 format
        :param tiles_count: count of tiles to wait after discard
        """
        self.player = player
        self.tile_to_discard = tile_to_discard
        self.waiting = waiting
        self.tiles_count = tiles_count

        self.calculate_value()

    def find_tile_in_hand(self, closed_hand):
        """
        Find and return 136 tile in closed player hand
        """

        # special case, to keep aka dora in hand
        if self.tile_to_discard in [4, 13, 22]:
            aka_closed_hand = closed_hand[:]
            while True:
                tile = TilesConverter.find_34_tile_in_136_array(self.tile_to_discard, aka_closed_hand)
                # we have only aka dora in the hand
                if not tile:
                    break

                # we found aka in the hand,
                # let's try to search another five tile
                # to keep aka dora
                if tile in AKA_DORA_LIST:
                    aka_closed_hand.remove(tile)
                else:
                    return tile

        return TilesConverter.find_34_tile_in_136_array(self.tile_to_discard, closed_hand)

    def calculate_value(self):
        # base is 100 for ability to mark tiles as not needed (like set value to 50)
        value = 100
        honored_value = 20

        # we don't need to keep honor tiles in almost completed hand
        if self.player.ai.previous_shanten <= 2:
            honored_value = 0

        if is_honor(self.tile_to_discard):
            if self.tile_to_discard in self.player.ai.valued_honors:
                count_of_winds = [x for x in self.player.ai.valued_honors if x == self.tile_to_discard]
                # for west-west, east-east we had to double tile value
                value += honored_value * len(count_of_winds)
        else:
            # suits
            suit_tile_grades = [10, 20, 30, 40, 50, 40, 30, 20, 10]
            simplified_tile = simplify(self.tile_to_discard)
            value += suit_tile_grades[simplified_tile]

        count_of_dora = plus_dora(self.tile_to_discard * 4, self.player.table.dora_indicators)
        value += 50 * count_of_dora

        self.value = value
